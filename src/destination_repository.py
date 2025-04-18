from abc import ABC, abstractmethod
from google.cloud import bigquery
from typing import List
from src import model


class AbstractDestinationRepository(ABC):
    """
    An abstract base class for destination repository interfaces that define methods to interact with a
    destination data storage in relation to Exchange Rates.

    Methods:
        load_exchange_rates(List[model.ExchangeRate]):
            interface to load Exchange Rates into the destination repository.
    """

    @abstractmethod
    def load_exchange_rates(self, exchange_rates: List[model.ExchangeRate]):
        """
        Abstract method to define the interface to load Exchange Rates into the
        destination repository.

        Args:
            exchange_rates (List[model.ExchangeRate]):
                List of ExchangeRate instances to be loaded into the repository.
        """
        raise NotImplementedError


class BiqQueryDestinationRepository(AbstractDestinationRepository):
    """
    A concrete implementation of the AbstractDestinationRepository to interact with Google BigQuery.
    This class is designed to load Exchange Rates data into Google BigQuery.

    Args:
        client (google.cloud.bigquery.Client): The BigQuery client instance.
    Attributes:
        client (google.cloud.bigquery.Client): The BigQuery client instance.
        exchange_rates_destination (str): The destination table for exchange rates in BigQuery.
    Methods:
        load_exchange_rates(List[model.ExchangeRate]):
            interface to load Exchange Rates into bq table indicated
            by attribute exchange_rates_destination.
    """

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.exchange_rates_destination = "raw.exchange_rates"

    def load_exchange_rates(self, exchange_rates: List[model.ExchangeRate]):
        """
        interface to load Exchange Rates into bq table indicatedby attribute
        exchange_rates_destination.

        Args:
            exchange_rates (List[model.ExchangeRate]):
                List of ExchangeRate instances to be loaded into BigQuery.
        """

        dictify = [
            {
                "date": exchange_rate.date.strftime("%Y-%m-%d"),
                "exchange_rate": exchange_rate.exchange_rate,
                "base_currency": exchange_rate.currency_pair.base,
                "quote_currency": exchange_rate.currency_pair.quote,
                "source": exchange_rate.source,
                "creation_date": exchange_rate.creation_date.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
            for exchange_rate in exchange_rates
        ]
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        load_job = self.client.load_table_from_json(
            dictify, self.exchange_rates_destination, job_config=job_config
        )
        load_job.result()
