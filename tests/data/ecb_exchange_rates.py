from src import model
import datetime as dt


ECB_EXCHANGE_RATES = [
    model.EcbExchangeRate(dt.date(2023, 10, 5), 0.866, "GBP"),
    model.EcbExchangeRate(dt.date(2023, 10, 6), 0.868, "GBP"),
    model.EcbExchangeRate(dt.date(2023, 10, 7), 0.870, "GBP"),
    model.EcbExchangeRate(dt.date(2023, 10, 8), 0.872, "GBP"),
    model.EcbExchangeRate(dt.date(2023, 10, 9), 0.873, "GBP"),
]
