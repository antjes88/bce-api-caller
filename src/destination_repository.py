from abc import ABC, abstractmethod
from google.cloud import bigquery
from typing import List
from src import model


class DestinationAbstractRepository(ABC):
    """
    An abstract base class for destination repository interfaces that define methods to interact with a
    destination data storage in relation to European Central Bank Exchange Rates.

    Methods:
        load_ecb_exchange_rates(List[model.EcbExchangeRate]):
            List of EcbExchangeRate instances to be loaded into the repository.
    """

    @abstractmethod
    def load_ecb_exchange_rates(self, ecb_exchange_rates: List[model.EcbExchangeRate]):
        """
        Abstract method to define the interface for loading ECB Exchange Rates into the
        destination repository.

        Args:
            ecb_exchange_rates (List[model.EcbExchangeRate]):
                List of EcbExchangeRate instances to be loaded into the repository.
        """
        raise NotImplementedError


class BiqQueryDestinationRepository(DestinationAbstractRepository):
    """
    A concrete implementation of the DestinationAbstractRepository to interact with Google BigQuery.
    This class is designed to load ECB Exchange Rates data into Google BigQuery.

    Args:
        client (google.cloud.bigquery.Client): The BigQuery client instance.
    Attributes:
        client (google.cloud.bigquery.Client): The BigQuery client instance.
        ecb_exchange_rates_destination (str): The destination table for ECB exchange rates in BigQuery.
    Methods:
        load_ecb_exchange_rates(ecb_rates: list[model.EcbExchangeRate]):
            Load ECB exchange rates into BigQuery table indicated by attribute ecb_exchange_rates_destination.
    """

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.ecb_exchange_rates_destination = "raw.ecb_exchange_rates"

    def load_ecb_exchange_rates(self, ecb_exchange_rates: List[model.EcbExchangeRate]):
        """
        Load ECB exchange rates into BigQuery table indicated by attribute ecb_exchange_rates_destination.

        Args:
            ecb_exchange_rates (List[model.EcbExchangeRate]): List of EcbExchangeRate instances to be loaded
                into BigQuery.
        """

        dictify = [
            {
                "date": ecb_rate.date.strftime("%Y-%m-%d"),
                "exchange_rate": ecb_rate.exchange_rate,
                "currency": ecb_rate.currency,
                "creation_date": ecb_rate.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for ecb_rate in ecb_exchange_rates
        ]
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        load_job = self.client.load_table_from_json(
            dictify, self.ecb_exchange_rates_destination, job_config=job_config
        )
        load_job.result()
