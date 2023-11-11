import pytest
from cloud_function.repository import BiqQueryRepository
from cloud_function import model
import os
from tests.data.ecb_rates import ECB_RATES
import datetime as dt


@pytest.fixture(scope="session")
def bq_repository():
    """
    Fixture that returns instance of BiqQueryRepository() instantiated with test parameters

    Returns:
        instance of BiqQueryRepository()
    """
    bq_repository = BiqQueryRepository(project=os.environ["PROJECT"])
    bq_repository.ecb_exchange_rates_destination = (
        os.environ["DATASET"] + "." + os.environ["DESTINATION_TABLE"]
    )

    return bq_repository


@pytest.fixture(scope="function")
def repository_with_ecb_rates(bq_repository):
    """
    Fixture that creates an ecb rates table and loads some dummy table on it on destination BigQuery project.
    Deletes table during tear down.

    Args:
        bq_repository: instance of BiqQueryRepository()

    Returns:
        instance of BiqQueryRepository() where a cashflow table has been created
    """
    bq_repository.load_ecb_exchange_rates(ECB_RATES)

    yield bq_repository, ECB_RATES

    bq_repository.client.delete_table(
        os.environ["DATASET"] + "." + os.environ["DESTINATION_TABLE"]
    )

@pytest.fixture(scope="function")
def fake_ecb_api():
    """
    Pytest fixture for providing a fake ECB API caller and expected ECB rates for testing purposes.
    This fixture creates an instance of EcbApiCallerFake with predefined API responses
    and generates a list of expected ECB rates for different currencies from given API responses.

    Returns:
        Tuple[EcbApiCallerFake, list[EcbRate]]: A tuple containing the fake ECB API caller
        and the list of expected ECB rates for testing.
    """
    api_responses = {
        "GBP": "tests/data/xml_ecb_test.xml",
        "USD": "tests/data/xml_ecb_test.xml",
    }
    fake_ecb_api_caller = model.EcbApiCallerFake(api_responses)

    expected_ecb_rates = [
        model.EcbExchangeRate(dt.date(2023, 11, 6), 0.8664, "GBP"),
        model.EcbExchangeRate(dt.date(2023, 11, 7), 0.86855, "GBP"),
        model.EcbExchangeRate(dt.date(2023, 11, 8), 0.87015, "GBP"),
        model.EcbExchangeRate(dt.date(2023, 11, 9), 0.87205, "GBP"),
        model.EcbExchangeRate(dt.date(2023, 11, 10), 0.87435, "GBP"),
        model.EcbExchangeRate(dt.date(2023, 11, 6), 0.8664, "USD"),
        model.EcbExchangeRate(dt.date(2023, 11, 7), 0.86855, "USD"),
        model.EcbExchangeRate(dt.date(2023, 11, 8), 0.87015, "USD"),
        model.EcbExchangeRate(dt.date(2023, 11, 9), 0.87205, "USD"),
        model.EcbExchangeRate(dt.date(2023, 11, 10), 0.87435, "USD"),
    ]

    return fake_ecb_api_caller, expected_ecb_rates, api_responses.keys()
