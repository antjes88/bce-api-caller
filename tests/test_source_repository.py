from src import model, source_repository
import datetime as dt
import requests as req
import requests_mock
import pytest


def test_reach_ecb_api():
    """
    GIVEN an instance of the EcbApiCaller()
    WHEN a call is sent to ecb api
    THEN a successful response has to be returned
    """
    ecb_api_caller = source_repository.EcbApiCaller(5)
    response = ecb_api_caller._call_to_ecb_api_exchange_rate("GBP")

    assert response.status_code == 200


def test_xml_to_ecb_rates():
    """
    GIVEN a response from a call to ecb api
    WHEN it is passed to EcbApiCaller.xml_to_ecb_rates()
    THEN a collection of EcbRate from the data in the
    """
    with open("tests/data/xml_ecb_test.xml", "r") as f:
        response_text = f.read()

    with requests_mock.Mocker() as mocker:
        url = "https://sdw-wsrest.ecb.europa.eu"
        mocker.get(url, text=response_text, status_code=200)
        response = req.get(url)

    result_ecb_rates = source_repository.EcbApiCaller._xml_to_ecb_rates(response, "GBP")

    expected_ecb_rates = [
        model.EcbExchangeRate(dt.date(2023, 11, 6), 0.8664, "GBP"),
        model.EcbExchangeRate(dt.date(2023, 11, 7), 0.86855, "GBP"),
        model.EcbExchangeRate(dt.date(2023, 11, 8), 0.87015, "GBP"),
        model.EcbExchangeRate(dt.date(2023, 11, 9), 0.87205, "GBP"),
        model.EcbExchangeRate(dt.date(2023, 11, 10), 0.87435, "GBP"),
    ]

    assert len(result_ecb_rates) == 5
    for expected_ecb_rate in expected_ecb_rates:
        assert expected_ecb_rate in result_ecb_rates


def test_get_ecb_rates(fake_ecb_api):
    """
    GIVEN a response from a call to ecb api
    WHEN it is passed to EcbApiCaller.xml_to_ecb_rates()
    THEN a collection of EcbRate from the data in the
    * note: used EcbApiCallerFake() to fake api connection
    """
    fake_ecb_api_caller, expected_ecb_rates, currencies = fake_ecb_api
    result_ecb_rates = fake_ecb_api_caller.get_ecb_rates(currencies)

    assert len(result_ecb_rates) == 10
    for expected_ecb_rate in expected_ecb_rates:
        assert expected_ecb_rate in result_ecb_rates


def test_get_ecb_rates_with_invalid_currency(fake_ecb_api):
    """
    GIVEN a EcbApiCaller instance with predefined responses
    WHEN get_ecb_rates is called with an invalid currency
    THEN a ValueError should be raised
    """
    fake_ecb_api_caller, _, _ = fake_ecb_api

    with pytest.raises(ValueError) as excinfo:
        fake_ecb_api_caller.get_ecb_rates(["INVALID"])

    assert "ECB API returned status code" in str(excinfo.value)
    assert "INVALID" in str(excinfo.value)
