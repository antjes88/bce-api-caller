from dataclasses import dataclass, field
import datetime as dt


@dataclass(frozen=True)
class CurrencyPair:
    """
    Represents a currency pair consisting of a base currency and a quote currency.

    Attributes:
        base (str): The base currency in the currency pair.
        quote (str): The quote currency in the currency pair.
    """

    base: str
    quote: str

    def __post_init__(self):
        object.__setattr__(self, "base", self.base.upper())
        object.__setattr__(self, "quote", self.quote.upper())
        if self.base == self.quote:
            raise ValueError("Base and quote currencies must be different.")

    def __str__(self):
        return f"{self.base}/{self.quote}"


@dataclass(frozen=True)
class ExchangeRate:
    """
    Data class representing exchange rates closing price.

    Attributes:
        date (datetime): Date of the exchange rate.
        exchange_rate (float): Exchange rate value.
        currency_pair (CurrencyPair): Currency pair (base/quote).
        to_currency (str): Currency. to_currency_amount = from_currency_amount / exchange_rate.
        source (str): Source of the exchange rate.
        creation_date (datetime): Creation date of the instance (default is the current date and time).
    """

    date: dt.date
    exchange_rate: float
    currency_pair: CurrencyPair
    source: str
    creation_date: dt.datetime = field(default_factory=dt.datetime.now)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ExchangeRate):
            return False
        return (
            self.date == other.date
            and self.exchange_rate == other.exchange_rate
            and self.currency_pair == other.currency_pair
            and self.source == other.source
        )
