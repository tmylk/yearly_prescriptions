import pytest

from prescriptions import download_and_process_one_month, download_and_process_dataset, stub, download_and_process_one_month, prep_db


@pytest.fixture(scope="session", autouse=True)
def app():
    with stub.run() as app:
        yield app
        

# def test_download_one_month():
#     l = download_one_month.call(month=1, year=2014)
    
#     assert len(l) > 0
#     assert l== 'EPD_201401'


# def test_aggregate_one_month():
#     l = aggregate_one_month.call(month=1, year=2014)
    
#     assert len(l) > 0
#     assert len(l) == 10000

# def test_download_and_process_one_month():
#     l = download_and_process_one_month.call(month=1, year=2014)
    
#     assert len(l) > 0
#     assert len(l) == 10000

# def test_prep_db():
#     l = prep_db.call()
#     assert l > 0


# def test_download_dataset():
#     l = download_dataset.call()
    
#     assert len(l) > 0
#     assert len(l) == 107
    


# def test_only_june_2022():
#     l = get_data.call()
#     for date, count in l:
#         assert date.month == 6
#         assert date.year == 2022