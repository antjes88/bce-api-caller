from dataclasses import dataclass
import datetime as dt


@dataclass(frozen=True)
class EcbExchangeRate:
    """
    Data class representing ECB exchange rates.

    Attributes:
        date (datetime): Date of the exchange rate.
        exchange_rate (float): Exchange rate value.
        currency (str): Currency for which the exchange rate is provided.
        creation_date (datetime): Creation date of the instance (default is the current date and time).
    """

    date: dt.date
    exchange_rate: float
    currency: str
    creation_date: dt.datetime = dt.datetime.now()

    def __eq__(self, other) -> bool:
        if not isinstance(other, EcbExchangeRate):
            return False
        return (
            self.date == other.date
            and self.exchange_rate == other.exchange_rate
            and self.currency == other.currency
        )
