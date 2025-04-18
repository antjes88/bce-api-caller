from abc import ABC, abstractmethod
from xml.etree import ElementTree as Et
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests as req
import requests_mock
import datetime as dt
from typing import List

from src import model


class AbstractSourceRepository(ABC):
    """
    An abstract base class for source repository interfaces that define methods to interact with a
    source data storage from where to extract Exchange Rates.

    Methods:
        get_exchange_rates(currency_pairs: List[model.CurrencyPair]) -> list[model.ExchangeRate]:
            Retrieves exchange rates for a list of currency pairs.
    """

    @abstractmethod
    def get_exchange_rates(
        self, currency_pairs: List[model.CurrencyPair]
    ) -> list[model.ExchangeRate]:
        """
        Retrieves exchange rates for a list of currency pairs.

        Args:
            currency_pairs (List[model.CurrencyPair]):
                currency pair consisting of a base currency and a quote currency.
        Returns:
            list[model.ExchangeRate]: A list of ExchangeRate instances.
        """
        raise NotImplementedError


class EcbApiCaller(AbstractSourceRepository):
    """
    Concrete implementation of AbstractSourceRepository to interact with the ECB API.
    This class provides methods to make API calls to the European Central Bank (ECB) API
    and process the XML response into a list of ExchangeRate instances.

    Args:
        days_to_register (int): Number of days to consider when making the API call. Default is 10.
    Attributes:
        days_to_register (int): Number of days to consider when making the API call. Default is 10.
    Methods:
        _call_to_ecb_api_exchange_rate(currency: str) -> Response:
            Calls the ECB API to get exchange rates for a specific currency pair.
        _xml_to_ecb_rates(response: req.models.Response, currency: str) -> list[model.ExchangeRate]:
            Converts an XML response from ECB API to a list of ExchangeRate instances.
        get_exchange_rates(currency_pairs: List[model.CurrencyPair]) -> list[model.ExchangeRate]:
            Retrieves exchange rates for a list of currency pairs.
    """

    def __init__(self, days_to_register: int = 10):
        self.days_to_register = days_to_register

    def _call_to_ecb_api_exchange_rate(
        self, currency_pair: model.CurrencyPair
    ) -> req.models.Response:
        """
        Calls the ECB API to get exchange rates for a specific currency pair.

        Args:
            currency_pair (model.CurrencyPair): The currency pair consisting to get exchange rates for.
        Returns:
            Response: The HTTP response object.
        """
        session = req.Session()
        retry = Retry(
            total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=0.1
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)

        ecb_url = (
            f"https://data-api.ecb.europa.eu/service/data/EXR/"
            f"D.{currency_pair.quote}.{currency_pair.base}.SP00.A"
            f"?startPeriod=%s&endPeriod=%s"
        )
        date_from = str(
            dt.datetime.date(dt.datetime.now()) - dt.timedelta(self.days_to_register)
        )
        date_to = str(dt.datetime.date(dt.datetime.now()))

        return session.get(ecb_url % (date_from, date_to))

    @staticmethod
    def _xml_to_ecb_rates(
        response: req.models.Response, currency_pair: model.CurrencyPair
    ) -> list[model.ExchangeRate]:
        """
        Converts an HTTP response from ECB API to a list of ExchangeRate instances.

        Args:
            response (req.models.Response): HTTP response from the ECB API.
            currency_pair (model.CurrencyPair): The currency pair from which exchange rates
                have been extracted.
        Returns:
            list[ExchangeRate]: A list of ExchangeRate instances.
        """
        exchange_rates = []
        root = Et.fromstring(response.text)
        for series in root.iter(
            "{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Series"
        ):
            for obs, value in zip(
                series.iter(
                    "{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs"
                ),
                series.iter(
                    "{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Value"
                ),
            ):
                date, exchange_rate = None, None
                for child in obs.iter():
                    if "ObsDimension" in child.tag:
                        date = dt.datetime.strptime(
                            child.attrib["value"], "%Y-%m-%d"
                        ).date()
                    elif "ObsValue" in child.tag:
                        exchange_rate = float(child.attrib["value"])

                if date and exchange_rate:
                    exchange_rates.append(
                        model.ExchangeRate(
                            date=date,
                            exchange_rate=exchange_rate,
                            currency_pair=currency_pair,
                            source="ECB API",
                        )
                    )

        return exchange_rates

    def get_exchange_rates(
        self, currency_pairs: List[model.CurrencyPair]
    ) -> list[model.ExchangeRate]:
        """
        Retrieves exchange rates for a list of currency pairs.

        Args:
            currency_pairs (List[model.CurrencyPair]):
                List of currency pairs consisting of a base currency and a quote currency.
        Returns:
            list[model.ExchangeRate]: A list of ExchangeRate instances.
        """
        for currency_pair in currency_pairs:
            if currency_pair.base != "EUR":
                raise ValueError(
                    "Base currency must be EUR for ECP API. "
                    "Please use the correct currency pair."
                )

        exchange_rates = []
        for currency_pair in currency_pairs:
            response = self._call_to_ecb_api_exchange_rate(currency_pair)

            if response.status_code != 200:
                raise ValueError(
                    f"ECB API returned status code {response.status_code} for currency pair {currency_pair}"
                )

            for exchange_rate in self._xml_to_ecb_rates(response, currency_pair):
                exchange_rates.append(exchange_rate)

        return exchange_rates


class EcbApiCallerFake(EcbApiCaller):
    """
    Fake implementation of EcbApiCaller for testing purposes. This class extends EcbApiCaller and overrides
    the _call_to_ecb_api_exchange_rate method to provide fake responses for testing without making actual API calls.

    Args:
        api_responses (dict): A dictionary mapping currency codes to file paths containing fake API response texts.
        days_to_register (int): Number of days to consider when making the fake API call. Default is 10.
    Attributes:
        api_responses (dict): A dictionary mapping currency codes to file paths containing fake API responses text.
        days_to_register (int): Number of days to consider when making the fake API call. Default is 10.
    Methods:
        _call_to_ecb_api_exchange_rate(currency: str) -> Response:
            Overrides the parent method to return a fake response based on the provided API responses.
        _xml_to_ecb_rates(response: req.models.Response, currency: str) -> list[model.ExchangeRate]:
            Converts an XML response from ECB API to a list of ExchangeRate instances.
        get_exchange_rates(currency_pairs: List[model.CurrencyPair]) -> list[model.ExchangeRate]:
            Retrieves exchange rates for a list of currency pairs.
    """

    def __init__(self, api_responses: dict[str, str], days_to_register: int = 10):
        super().__init__(days_to_register=days_to_register)
        self.api_responses = api_responses

    def _call_to_ecb_api_exchange_rate(
        self, currency_pair: model.CurrencyPair
    ) -> req.models.Response:
        """
        Overrides the parent method to return a fake response based on the provided API responses.

        Args:
            currency_pairs (model.CurrencyPair):
                currency pair consisting of a base currency and a quote currency.
        Returns:
            Response: The fake HTTP response object.
        """
        url = "https://data-api.ecb.europa.eu"
        if currency_pair.quote not in self.api_responses.keys():
            with requests_mock.Mocker() as mocker:
                mocker.get(url, text="not valid", status_code=404)
                response = req.get(url)
        else:
            with open(self.api_responses[currency_pair.quote], "r") as f:
                response_text = f.read()
            with requests_mock.Mocker() as mocker:
                mocker.get(url, text=response_text, status_code=200)
                response = req.get(url)

        return response
