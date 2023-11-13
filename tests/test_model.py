from cloud_function import model
import datetime as dt
import pytest
import requests as req
import requests_mock


def test_ecb_rate_to_dict():
    """
    GIVEN an ecb rate
    WHEN it is converted to dict
    THEN it should return the expected result
    """
    date = dt.datetime.now().date()
    exchange_rate = 0.05
    currency = "GBP"
    creation_date = dt.datetime.now()

    assert model.EcbExchangeRate(
        date, exchange_rate, currency, creation_date
    ).to_dict() == {
        "date": date.strftime("%Y-%m-%d"),
        "exchange_rate": exchange_rate,
        "currency": currency,
        "creation_date": creation_date.strftime("%Y-%m-%d %H:%M:%S"),
    }


def test_ecb_rate_equality():
    """
    GIVEN 2 ecb rates that have same
    WHEN they are checked for equality
    THEN the result should be that both ecb rates are equal
    """
    date = dt.date(2021, 10, 10)
    exchange_rate = 0.05
    currency = "GBP"

    assert model.EcbExchangeRate(
        date,
        exchange_rate,
        currency,
        dt.datetime(
            1990,
            1,
            1,
        ),
    ) == model.EcbExchangeRate(
        date,
        exchange_rate,
        currency,
        dt.datetime(
            2020,
            12,
            12,
        ),
    )


@pytest.mark.parametrize(
    "date_left, date_right, exchange_rate_left, exchange_rate_right, currency_left, currency_right",
    [
        (dt.datetime(2021, 10, 10), dt.datetime(1990, 10, 10), 0.1, 0.1, "GBP", "GBP"),
        (dt.datetime(1990, 10, 10), dt.datetime(1990, 10, 10), 0.1, 0.2, "GBP", "GBP"),
        (dt.datetime(1990, 10, 10), dt.datetime(1990, 10, 10), 0.2, 0.2, "USD", "GBP"),
    ],
)
def test_ecb_rate_inequality(
    date_left,
    date_right,
    exchange_rate_left,
    exchange_rate_right,
    currency_left,
    currency_right,
):
    """
    GIVEN 2 ecb rates with different dates, exchange rates or currency
    WHEN they are checked for equality
    THEN the result should be that both ecb rates are NOT equal
    """
    creation_date = dt.datetime(
        1990,
        1,
        1,
    )

    assert model.EcbExchangeRate(
        date_left, exchange_rate_left, currency_left, creation_date
    ) != model.EcbExchangeRate(
        date_right, exchange_rate_right, currency_right, creation_date
    )


@pytest.mark.parametrize("value", [1, "string", 0.1, dt.datetime.now()])
def test_ecb_rate_inequality_other(value):
    """
    GIVEN an ecb rates and another data structure
    WHEN they are checked for equality
    THEN the result should be that both ecb rates are NOT equal
    """
    assert model.EcbExchangeRate(dt.datetime.now(), 0.1, "GBP") != value


def test_reach_ecb_api():
    """
    GIVEN an instance of the EcbApiCaller()
    WHEN a call is sent to ecb api
    THEN a successful response has to be returned
    """
    ecb_api_caller = model.EcbApiCaller(5)
    response = ecb_api_caller.call_to_ecb_api_exchange_rate("GBP")

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

    result_ecb_rates = model.EcbApiCaller.xml_to_ecb_rates(response, "GBP")

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
