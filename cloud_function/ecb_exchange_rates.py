import os
import requests as req
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from xml.etree import ElementTree as Et
from postgresql_interface.postgresql_interface import postgres_sql_connector_factory
import datetime as dt


def call_to_ecb_api_exchange_rate(days_to_register):
    """
    Function that calls to ecb api to obtain the eur change rates.

    Args:
        days_to_register: days going back from today.
            Obtaining from (today - days_to_register) to (today)
    Returns: response from ecb api
    """
    session = req.Session()
    retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=0.1)  # Reach 186 secs
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    ecb_url = "https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.GBP+USD.EUR.SP00.A/?startPeriod=%s&endPeriod=%s"
    date_from = str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days_to_register))
    date_to = str(dt.datetime.date(dt.datetime.now()))

    return session.get(ecb_url % (date_from, date_to))


def from_xml_to_dataframe(ecb_api_response):
    """
    Function that parse the response from ECB API to a dataframe with schema as PostgreSQL table
    bce.EuroaRatio

    Args:
        ecb_api_response: text response from ECB exchange rate API
    Returns: pandas dataframe with schema as PostgreSQL table bce.EuroaRatio
    """
    root = Et.fromstring(ecb_api_response)

    exchange_df = pd.DataFrame()
    for serie in root.iter('{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Series'):
        df = pd.DataFrame()
        for obs in serie.iter('{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs'):
            date, exchange_rate = None, None
            for child in obs.iter():
                if 'ObsDimension' in child.tag:
                    date = child.attrib['value']
                if 'ObsValue' in child.tag:
                    exchange_rate = float(child.attrib['value'])
            if date and exchange_rate:
                df = df.append(pd.DataFrame({'fecha': [date], 'Value': [exchange_rate]}))

        for value in serie.iter('{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Value'):
            if value.attrib['id'] == "CURRENCY":
                df['CurrencyISOCode'] = value.attrib['value']

        exchange_df = exchange_df.append(df).reset_index(drop=True)

    exchange_df = exchange_df.pivot(
        index='fecha', columns='CurrencyISOCode', values='Value').reset_index(
            ).rename(columns={'GBP': 'libra', 'USD': 'dolar'})

    exchange_df['createdby'] = 'System'
    exchange_df['created'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    exchange_df = exchange_df[exchange_df['libra'].notna()]
    exchange_df = exchange_df[exchange_df['dolar'].notna()]

    return exchange_df


def load_to_database_eur_exchange_rate(exchange_df):
    """
    Function that loads into landing table bce.EuroaRatio exchange_df dataframe which has been parsed
    from the response of the ECB Api by from_xml_to_dataframe() function. The function not only insert new dates
    but also updates the ones that could have been previously populated.

    Args:
        exchange_df: pandas dataframe that is the response from the ECB API exchange rate parse by function
            from_xml_to_dataframe()
    """
    db_conn = postgres_sql_connector_factory(
        vendor='gcp', host=os.environ['SERVER_HOST'], database_name=os.environ['DATABASE_NAME'],
        user_name=os.environ['USER_NAME'], user_password=os.environ['USER_PASSWORD'],
        port=os.environ['DATABASE_PORT_N'])
    db_conn.delete_from_table('bce.EuroaRatio', exchange_df['fecha'].to_frame())
    db_conn.insert_table('bce.EuroaRatio', exchange_df)
