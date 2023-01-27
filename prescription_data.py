import pandas as pd


def get_antibac_prescription_data():
    return  "5.1: Antibacterial drugs",  "https://openprescribing.net/bnf/0501/", "bnf_section_code = '0501'", 'spending-0501.csv',

def get_penicillins_prescription_data():
    return "5.1.1: Penicillins", 'https://openprescribing.net/bnf/050101/',  "bnf_subsection_code = '050101'",'spending-050101.csv'

def get_amoxicillin_prescription_data():
    return "Amoxicillin (0501013B0)",  'https://openprescribing.net/chemical/0501013B0/', "bnf_code like '0501013B0%%'",  'spending-0501013B0.csv'

def get_antifungal_prescription_data():
    return "5.2: Antifungal drugs",  'https://openprescribing.net/bnf/0502/', "bnf_section_code = '0502'", 'spending-0502.csv',

def get_infection_data():
    return "5: Infections",  'https://openprescribing.net/bnf/05/',  "bnf_chapter_code = '05'", 'spending-05.csv',

def export_prescription_data(filename):

    # select 

    df  = pd.read_csv(f'data/{filename}')
    c = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    df.date = pd.to_datetime(df.date)
    df = df.set_index('date')

    c = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['months'] = pd.CategoricalIndex(df.index.strftime('%b'), ordered=True, categories=c)
    df['years'] = df.index.year
    df_pivoted = df.pivot(index='months', columns='years',values='items')
    return df_pivoted


def get_prescription_data(filename):

    df  = pd.read_csv(f'data/{filename}')
    c = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    df.date = pd.to_datetime(df.date)
    df = df.set_index('date')

    c = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['months'] = pd.CategoricalIndex(df.index.strftime('%b'), ordered=True, categories=c)
    df['years'] = df.index.year
    df_pivoted = df.pivot(index='months', columns='years',values='ItemsPer1000')
    return df_pivoted
