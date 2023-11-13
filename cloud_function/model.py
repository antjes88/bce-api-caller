from xml.etree import ElementTree as Et
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests as req
import requests_mock
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
    Methods:
        to_dict() -> dict: Converts the instance data to a dictionary.
    """

    date: dt.date
    exchange_rate: float
    currency: str
    creation_date: dt.datetime = dt.datetime.now()

    def to_dict(self) -> dict:
        """
        Converts the instance data to a dictionary.

        Returns:
            dict: A dictionary representation of the instance data.
        """
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "exchange_rate": self.exchange_rate,
            "currency": self.currency,
            "creation_date": self.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __eq__(self, other) -> bool:
        if not isinstance(other, EcbExchangeRate):
            return False
        return (
            self.date == other.date
            and self.exchange_rate == other.exchange_rate
            and self.currency == other.currency
        )


class EcbApiCaller:
    """
    Class for calling the ECB API and processing exchange rate data. This class provides methods to make API calls to
    the European Central Bank (ECB) API and process the XML response into a list of EcbExchangeRate instances.

    Args:
        days_to_register (int): Number of days to consider when making the API call. Default is 10.
    Attributes:
        days_to_register (int): Number of days to consider when making the API call. Default is 10.
    Methods:
        call_to_ecb_api_exchange_rate(currency: str) -> Response:
            Calls the ECB API to get exchange rates for a specific currency.
        xml_to_ecb_rates(response: str, currency: str) -> list[EcbExchangeRate]:
            Converts an XML response from ECB API to a list of EcbExchangeRate instances.
    """

    def __init__(self, days_to_register: int = 10):
        self.days_to_register = days_to_register

    def call_to_ecb_api_exchange_rate(self, currency: str) -> req.models.Response:
        """
        Calls the ECB API to get exchange rates for a specific currency.

        Args:
            currency (str): The currency code for which to retrieve exchange rates.
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
            f"https://sdw-wsrest.ecb.europa.eu/service/data/EXR/"
            f"D.{currency}.EUR.SP00.A/?startPeriod=%s&endPeriod=%s"
        )
        date_from = str(
            dt.datetime.date(dt.datetime.now()) - dt.timedelta(self.days_to_register)
        )
        date_to = str(dt.datetime.date(dt.datetime.now()))

        return session.get(ecb_url % (date_from, date_to))

    @staticmethod
    def xml_to_ecb_rates(
        response: req.models.Response, currency: str
    ) -> list[EcbExchangeRate]:
        """
        Converts an HTTP response from ECB API to a list of EcbExchangeRate instances.

        Args:
            response (str): HTTP response from the ECB API.
            currency (str): The currency code for which rates are being processed.
        Returns:
            list[EcbExchangeRate]: A list of EcbExchangeRate instances.
        """
        ecb_exchange_rates = []
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
                    ecb_exchange_rates.append(
                        EcbExchangeRate(date, exchange_rate, currency)
                    )

        return ecb_exchange_rates

    def get_ecb_rates(self, currencies: list[str]) -> list[EcbExchangeRate]:
        """
        Retrieves ECB exchange rates for a list of currencies.

        Args:
            currencies (list[str]): List of currency codes for which to retrieve exchange rates.
        Returns:
            list[EcbExchangeRate]: A list of EcbExchangeRate instances.
        """
        ecb_exchange_rates = []
        for currency in currencies:
            response = self.call_to_ecb_api_exchange_rate(currency)
            for ecb_exchange_rate in self.xml_to_ecb_rates(response, currency):
                ecb_exchange_rates.append(ecb_exchange_rate)

        return ecb_exchange_rates


class EcbApiCallerFake(EcbApiCaller):
    """
    Fake implementation of EcbApiCaller for testing purposes. This class extends EcbApiCaller and overrides
    the call_to_ecb_api_exchange_rate method to provide fake responses for testing without making actual API calls.

    Args:
        api_responses (dict): A dictionary mapping currency codes to file paths containing fake API response texts.
        days_to_register (int): Number of days to consider when making the fake API call. Default is 10.
    Attributes:
        api_responses (dict): A dictionary mapping currency codes to file paths containing fake API responses text.
        days_to_register (int): Number of days to consider when making the fake API call. Default is 10.
    Methods:
        call_to_ecb_api_exchange_rate(currency: str) -> Response:
            Overrides the parent method to return a fake response based on the provided API responses.
    """

    def __init__(self, api_responses: dict[str:str], days_to_register: int = 10):
        super().__init__(days_to_register=days_to_register)
        self.api_responses = api_responses

    def call_to_ecb_api_exchange_rate(self, currency: str) -> req.models.Response:
        """
        Overrides the parent method to return a fake response based on the provided API responses.

        Args:
            currency (str): The currency code for which to retrieve exchange rates.
        Returns:
            Response: The fake HTTP response object.
        """
        with open(self.api_responses[currency], "r") as f:
            response_text = f.read()
        with requests_mock.Mocker() as mocker:
            url = "https://sdw-wsrest.ecb.europa.eu"
            mocker.get(url, text=response_text, status_code=200)
            response = req.get(url)

        return response
