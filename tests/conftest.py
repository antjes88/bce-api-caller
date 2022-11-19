# public libraries
import pytest
import os
from postgresql_interface.postgresql_interface import postgres_sql_connector_factory


@pytest.fixture(scope='session')
def db_conn():
    """
    Fixture that returns connector to database.

    Returns: API to interact with database in a sql manner.
    """
    return postgres_sql_connector_factory(
        vendor='gcp', host=os.environ['HOST'], database_name=os.environ['DATABASE_NAME'],
        user_name=os.environ['USER_NAME'], user_password=os.environ['USER_PASSWORD'], port=os.environ['DATABASE_PORT'])


@pytest.fixture(scope='function')
def truncate_ecb_eur_exchange_rate(db_conn):
    """
    Fixture that ensures that bce.EuroaRatio is truncated before and after the test.

    Args:
        db_conn: call to fixture that creates connector to db
    """
    db_conn.execute("TRUNCATE TABLE bce.EuroaRatio")
    yield
    db_conn.execute("TRUNCATE TABLE bce.EuroaRatio")
