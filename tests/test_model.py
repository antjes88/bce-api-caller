from src import model
import datetime as dt
import pytest


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
