from cloud_function.ecb_exchange_rates import from_xml_to_dataframe, call_to_ecb_api_exchange_rate, \
    load_to_database_eur_exchange_rate
import os
import pandas as pd
import datetime as dt


def test_from_xml_to_dataframe():
    """
    GIVEN an answer from ECB API
    WHEN it is processed by function from_xml_to_dataframe()
    THEN it should be the equal to result_expected_from_xml
    """
    with open(os.path.join(os.getcwd(), 'tests/data/xml_ecb_test.xml')) as f:
        exchange_rates = from_xml_to_dataframe(f.read())

    # this column is created with the datetime of the moment so cannot be compared
    exchange_rates.drop(columns=['created'], inplace=True)

    data = {
        "fecha": ["2021-05-26", "2021-05-27", "2021-05-28"],
        "libra": [0.8633, 0.86068, 0.85765],
        "dolar": [1.2229, 1.2198, 1.2142],
        "createdby": ["System", "System", "System"],
    }
    result_expected_from_xml = pd.DataFrame(data)

    assert exchange_rates.equals(result_expected_from_xml), "Check xml is correctly parsed to df"


def test_load_to_database_eur_exchange_rate(truncate_ecb_eur_exchange_rate, db_conn):
    """
    GIVEN a dataframe parsed from ECB Api Response
    WHEN it is loaded by function load_to_database_eur_exchange_rate() to the destination database
    THEN check that the data is correctly uploaded to the landing table
    """
    data = {
        'fecha': ['2021-05-26', '2021-05-27', '2021-05-28'],
        'libra': [0.8633, 0.86068, 0.85765],
        'dolar': [1.2229, 1.2198, 1.2142],
        'created': ['2022-11-17', '2022-11-17', '2022-11-17'],
        'createdby': ['System', 'System', 'System']
    }
    expected = pd.DataFrame(data)
    load_to_database_eur_exchange_rate(expected)
    result = db_conn.query("SELECT * FROM bce.EuroaRatio")

    for col in ['libra', 'dolar']:
        result[col] = result[col].apply(lambda x: round(x, 4))
        expected[col] = expected[col].apply(lambda x: round(x, 4))
    for col in ['fecha', 'created']:
        result[col] = result[col].apply(lambda x: dt.datetime.strftime(x, '%Y-%m-%d'))

    assert result.equals(expected), "Check df is correctly populated into landing table"


def test_call_to_ecb_api_exchange_rate():
    """
    GIVEN the ECB API
    WHEN a request is sent through the function call_to_ecb_api_exchange_rate()
    THEN check that the response is satisfactory
    """
    days_to_register = 10
    response = call_to_ecb_api_exchange_rate(days_to_register)

    assert response.status_code == 200, "Check ECB API is correctly reached"
