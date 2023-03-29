import asyncio
import os
import pathlib
import shutil
import tempfile
from datetime import datetime, timedelta

import modal
import requests

from prescription_data import get_graphs

stub = modal.Stub("prescription-data")
datasette_image = (
    modal.Image.debian_slim()
    .pip_install(
        "datasette~=0.63.2",
        "flufl.lock",
        "GitPython",
        "sqlite-utils",
        "requests", 
        "duckdb", "pandas", "sqlalchemy", "pyarrow", "sqlite-sqlean"
    )
    
)


volume = modal.SharedVolume().persist("prescriptions-dataset-cache-vol")

CACHE_DIR = "/cache"
TEMP_DIR = "/root"
LOCK_FILE = str(pathlib.Path(CACHE_DIR, "lock-reports"))
DATA_DIR = pathlib.Path(TEMP_DIR, "data")
AGG_DATA_DIR = pathlib.Path(CACHE_DIR, "agg_data")
DB_PATH = pathlib.Path(CACHE_DIR, "prescriptions.db")



def get_month_file(year=2022, month=11):
    target_file = "EPD_{year}{month:02d}".format(year=year, month=month)
    fullpath = pathlib.Path(DATA_DIR, target_file)
    return fullpath, target_file


@stub.function(interactive=False,
    image=datasette_image,
    shared_volumes={CACHE_DIR: volume},
    retries=2,timeout=1200
)
def download_and_process_one_month(year=2022, month=11):

    fullpath, target_file = get_month_file(year, month)

    from flufl.lock import Lock

    fullpath, target_file = get_month_file(year, month)

    locks_dir = pathlib.Path(CACHE_DIR, "locks")
    if not os.path.exists(locks_dir):
        os.mkdir(locks_dir)

    lock_file = str(pathlib.Path(CACHE_DIR, "locks",target_file + ".lck"))

    with Lock(
        lock_file, lifetime=timedelta(minutes=2), default_timeout=timedelta(hours=1)
    ) as lck:

        print(f"Starting {target_file}")
        agg_file =  pathlib.Path(AGG_DATA_DIR, f'{target_file}.parquet')
        if agg_file.exists():
            print(f"Dataset {target_file} already downloaded aggregated. Skipping download.")
            return target_file
        if not os.path.exists(DATA_DIR):
            os.mkdir(DATA_DIR)

        rsp = requests.get(
                "https://opendata.nhsbsa.net/api/3/action/package_show?id=english-prescribing-data-epd"
            )
        resources = rsp.json()["result"]["resources"]
        urls = [
                r["url"]
                for r in resources
                if r["name"] == target_file
            ]
        assert len(urls) == 1, urls
        rsp = requests.get(urls[0], stream=True)
        assert rsp.ok    

        with open(fullpath, "wb") as f:
                for block in rsp.iter_content(32 * 1024):
                    f.write(block)
        print(f"Downloaded {target_file}")

        
        import duckdb
        print("aggregating", fullpath, "...")

        con = duckdb.connect(database=":memory:")

        # !wc -l /cache/data/EPD_201401

        load_sql = f"""
            CREATE TABLE month_raw_data AS
            SELECT * FROM 
            read_csv_auto('{DATA_DIR}/{target_file}');        
        """
        # import IPython
        # IPython.embed()

        con.execute(load_sql)


        agg_sql = f"""
        CREATE TABLE agg_month_raw_data AS
        SELECT
            BNF_CODE AS bnf_code,
            BNF_CHAPTER_PLUS_CODE AS bnf_chapter,
            LEFT(BNF_CODE, 2) AS bnf_chapter_code,
            LEFT(BNF_CODE, 4) AS bnf_section_code,
            LEFT(BNF_CODE, 6) AS bnf_subsection_code,
            BNF_DESCRIPTION AS bnf_name,
            SUM(ITEMS) AS items,
            SUM(NIC) AS net_cost,
            SUM(ACTUAL_COST) AS actual_cost,
            SUM(TOTAL_QUANTITY) AS quantity,
            make_date({year},{month},1) AS month
            FROM 
            month_raw_data
            WHERE PRACTICE_CODE NOT LIKE '%%998'  -- see issue #349
            GROUP BY
            bnf_code,bnf_chapter,bnf_chapter_code, bnf_section_code, bnf_subsection_code, bnf_name"""
        con.execute(agg_sql)
        # Append aggregated data to prescribing table
        export_sql = f"COPY agg_month_raw_data TO '{AGG_DATA_DIR}/{target_file}.parquet'  (FORMAT PARQUET);" 
        if not os.path.exists(AGG_DATA_DIR):
            os.mkdir(AGG_DATA_DIR)


        con.execute(export_sql)

        # # import IPython
        # # IPython.embed()
        # # run in ipython:
        # # my_df = con.df()
        # # my_df.d.apply(lambda x:x.year).value_counts()
        print("Finished aggregating ", fullpath, ".")

        
        
        
        return fullpath


    
@stub.function(
    image = datasette_image, timeout=86400
)
def download_and_process_dataset():
    inputs = [(year, month) for year in range(2014, 2024) for month in range(1, 13) if (year, month) <= (2023, 1)]
    l = []   
    for r in download_and_process_one_month.starmap(inputs):
        print(r)
        l.append(r)
    return l




@stub.function(
    image=datasette_image,
    shared_volumes={CACHE_DIR: volume},
    timeout=900,interactive=False
)
def prep_db():
    def read_population_table():
        import pandas as pd

        # uploaded with modal volume put prescriptions-dataset-cache-vol pop.csv
        df = pd.read_csv(os.path.join(CACHE_DIR,'pop.csv'), skiprows=[0,2,3,4,5,6])
        df['year'] = df.CDID
        df['population'] = df.ENPOP
        df = df[['year','population']]
        df = df.append({'year':2022, 'population':56550138}, ignore_index=True)
        df = df.append({'year':2023, 'population':56550138}, ignore_index=True)
        return df

    #import sqlite_utils
    import glob
    import sqlite3

    import pandas as pd
    from flufl.lock import Lock

    print("Loading all months")

    with Lock(
        LOCK_FILE, lifetime=timedelta(minutes=2), default_timeout=timedelta(hours=1)
    ) as lck, tempfile.NamedTemporaryFile() as tmp:
        conn = sqlite3.connect(tmp.name)


        for parquet_file in glob.glob(f"{AGG_DATA_DIR}/*.parquet"):
            print(parquet_file)
            df = pd.read_parquet(parquet_file)
#            import IPython
#           IPython.embed()

            
            df['year'] = df.month.apply(lambda x: x.year)
            df_population = read_population_table()

            df_merged = pd.merge(df,df_population,how='inner',left_on=['year'],right_on=['year'])

            
            df_merged.to_sql("prescriptions", conn, if_exists='append', index=False)

        conn.commit()

#         import IPython
#         IPython.embed()
# cur = conn.cursor()
# res = cur.execute("SELECT * FROM prescriptions")
# res.fetchall()

        # table.create_index(["day"], if_not_exists=True)
        # table.create_index(["province_or_state"], if_not_exists=True)
        # table.create_index(["country_or_region"], if_not_exists=True)

        print("Syncing DB with shared volume.")
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(tmp.name, DB_PATH)



@stub.function(
    image = datasette_image, timeout=86400
)
def download_and_process_dataset_and_db():
    download_and_process_dataset.call()
    prep_db.call()

# uncomment when have db
@stub.asgi(
    image=datasette_image,
    shared_volumes={CACHE_DIR: volume},
)
def app():
    from datasette.app import Datasette

    ds = Datasette(files=[DB_PATH], settings = {'sql_time_limit_ms': 3500})
    asyncio.run(ds.invoke_startup())
    return ds.app()

# ## Publishing to the web
#
# Run this script using `modal run prescriptions.py` and it will create the database.
#
#
# When publishing the interactive Datasette app you'll want to create a persistent URL.
# This is achieved by deploying the script with `modal deploy prescriptions.py`.


@stub.function(
    image = datasette_image, timeout=60, shared_volumes={CACHE_DIR: volume},
)
def extract_specific_codes():


    # def add_population_table_to_db(conn):
    #     df = read_population_table()
    #     df.to_sql("population", conn, if_exists='replace', index=False)


    import sqlite3

    import pandas as pd
    import sqlite_sqlean
    conn = sqlite3.connect(DB_PATH )
    conn.enable_load_extension(True)
    
    sqlite_sqlean.load(conn, 'regexp')
    l = []
    for name, url, condition, filename in get_graphs():
       
        df = pd.read_sql_query(f"""SELECT month as date, SUM(ITEMS) AS items, 1000*SUM(items)/population AS ItemsPer1000  FROM prescriptions WHERE {condition} GROUP BY month
        
        """, conn)
        df.to_sql(filename.split('.')[0], conn, if_exists='replace', index=False)
        l.append((filename, df.copy()))
    conn.commit()
    return l





OUTPUT_DIR = "data"

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with stub.run():
        dfs = extract_specific_codes.call()
        for filename, df in dfs:
            fn = os.path.join(OUTPUT_DIR, filename)
            df.to_csv(fn)
            print(f"wrote output to {fn}")
