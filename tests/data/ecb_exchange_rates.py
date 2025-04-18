from src import model
from typing import List
import datetime as dt


EXCHANGE_RATES: List[model.ExchangeRate] = [
    model.ExchangeRate(
        date=dt.date(2023, 10, 5),
        exchange_rate=0.866,
        currency_pair=model.CurrencyPair("EUR", "GBP"),
        source="ECB API",
    ),
    model.ExchangeRate(
        date=dt.date(2023, 10, 6),
        exchange_rate=0.868,
        currency_pair=model.CurrencyPair("EUR", "GBP"),
        source="ECB API",
    ),
    model.ExchangeRate(
        date=dt.date(2023, 10, 7),
        exchange_rate=0.870,
        currency_pair=model.CurrencyPair("EUR", "GBP"),
        source="ECB API",
    ),
    model.ExchangeRate(
        date=dt.date(2023, 10, 8),
        exchange_rate=0.872,
        currency_pair=model.CurrencyPair("EUR", "GBP"),
        source="ECB API",
    ),
    model.ExchangeRate(
        date=dt.date(2023, 10, 9),
        exchange_rate=0.873,
        currency_pair=model.CurrencyPair("EUR", "GBP"),
        source="ECB API",
    ),
]
