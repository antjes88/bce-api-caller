from typing import Tuple, List
import datetime as dt
import requests as req
import requests_mock
import pytest

from src import model, source_repository


def test_reach_ecb_api():
    """
    GIVEN an instance of the EcbApiCaller()
    WHEN a call is sent to ecb api
    THEN a successful response has to be returned
    """
    ecb_api_caller = source_repository.EcbApiCaller(5)
    response = ecb_api_caller._call_to_ecb_api_exchange_rate(
        model.CurrencyPair("EUR", "GBP")
    )

    assert response.status_code == 200


def test_xml_to_ecb_rates():
    """
    GIVEN a response from a call to ecb api
    WHEN it is passed to EcbApiCaller.xml_to_ecb_rates()
    THEN it should returns the expected list of ExchangeRate objects
    """
    with open("tests/data/xml_ecb_test.xml", "r") as f:
        response_text = f.read()

    with requests_mock.Mocker() as mocker:
        url = "https://data-api.ecb.europa.eu"
        mocker.get(url, text=response_text, status_code=200)
        response = req.get(url)

    result_ecb_rates = source_repository.EcbApiCaller._xml_to_ecb_rates(
        response, model.CurrencyPair("EUR", "GBP")
    )

    expected_ecb_rates = [
        model.ExchangeRate(
            date=dt.date(2023, 11, 6),
            exchange_rate=0.8664,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 7),
            exchange_rate=0.86855,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 8),
            exchange_rate=0.87015,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 9),
            exchange_rate=0.87205,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
        model.ExchangeRate(
            date=dt.date(2023, 11, 10),
            exchange_rate=0.87435,
            currency_pair=model.CurrencyPair("EUR", "GBP"),
            source="ECB API",
        ),
    ]

    assert len(result_ecb_rates) == 5
    for expected_ecb_rate in expected_ecb_rates:
        assert expected_ecb_rate in result_ecb_rates


def test_get_ecb_rates(
    fake_ecb_api: Tuple[
        source_repository.EcbApiCallerFake,
        List[model.ExchangeRate],
        List[model.CurrencyPair],
    ],
):
    """
    GIVEN a response from a call to ecb api
    WHEN it is passed to EcbApiCaller.xml_to_ecb_rates()
    THEN it should returns the expected list of ExchangeRate objects
    * note: used EcbApiCallerFake() to fake api connection
    """
    fake_ecb_api_caller, expected_ecb_rates, currency_pairs = fake_ecb_api
    result_ecb_rates = fake_ecb_api_caller.get_exchange_rates(currency_pairs)

    assert len(result_ecb_rates) == 10
    for expected_ecb_rate in expected_ecb_rates:
        assert expected_ecb_rate in result_ecb_rates


def test_get_ecb_rates_with_invalid_currency(
    fake_ecb_api: Tuple[
        source_repository.EcbApiCallerFake,
        List[model.ExchangeRate],
        List[model.CurrencyPair],
    ],
):
    """
    GIVEN a EcbApiCaller instance with predefined responses
    WHEN get_ecb_rates is called with an invalid currency
    THEN a ValueError should be raised
    """
    fake_ecb_api_caller, _, _ = fake_ecb_api

    with pytest.raises(ValueError) as excinfo:
        fake_ecb_api_caller.get_exchange_rates([model.CurrencyPair("EUR", "INVALID")])

    assert "ECB API returned status code" in str(excinfo.value)
    assert "INVALID" in str(excinfo.value)


def test_get_ecb_rates_with_base_currency_not_eur(
    fake_ecb_api: Tuple[
        source_repository.EcbApiCallerFake,
        List[model.ExchangeRate],
        List[model.CurrencyPair],
    ],
):
    """
    GIVEN a EcbApiCaller instance with predefined responses
    WHEN get_ecb_rates is called with a base currency that is not EUR
    THEN a ValueError should be raised
    """
    fake_ecb_api_caller, _, _ = fake_ecb_api

    with pytest.raises(ValueError) as excinfo:
        fake_ecb_api_caller.get_exchange_rates([model.CurrencyPair("USD", "EUR")])

    expected_error_message = (
        "Base currency must be EUR for ECP API. "
        "Please use the correct currency pair."
    )

    assert expected_error_message in str(excinfo.value)
