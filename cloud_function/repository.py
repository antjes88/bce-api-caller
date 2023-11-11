from abc import ABC, abstractmethod
from google.cloud import bigquery
import model


class AbstractRepository(ABC):
    """
    An abstract base class for repository interfaces that define methods to interact with a data source.
    Subclasses of AbstractRepository are expected to implement these methods to handle data storage.

    Methods:
        load_ecb_exchange_rates(List[model.EcbExchangeRate]): List of EcbExchangeRate instances to be loaded into the
            repository.
    """
    @abstractmethod
    def load_ecb_exchange_rates(self, ecb_exchange_rates: list[model.EcbExchangeRate]):
        """
        Abstract method to define the interface for loading ECB Exchange Rates into the repository.

        Args:
            ecb_exchange_rates (List[model.EcbExchangeRate]): List of EcbExchangeRate instances to be loaded into
                the repository.
        """
        raise NotImplementedError


class BiqQueryRepository(AbstractRepository):
    """
    A concrete implementation of the AbstractRepository for interacting with Google BigQuery.
    This repository class is designed to load ECB Exchange Rates data into Google BigQuery.

    Args:
        project (str, optional): The Google Cloud project ID. Defaults to None.
    Attributes:
        client (google.cloud.bigquery.Client): The BigQuery client instance.
        ecb_exchange_rates_destination (str): The destination table for ECB exchange rates in BigQuery.
    Methods:
        load_table_from_json(data: list[dict], destination: str, job_config: bigquery.job.load.LoadJobConfig):
            Load data from a list of dictionaries into a BigQuery table.
        load_ecb_exchange_rates(ecb_rates: list[model.EcbExchangeRate]):
            Load ECB exchange rates into BigQuery table indicated by attribute ecb_exchange_rates_destination.
    """
    def __init__(self, project=None):
        self.client = bigquery.Client(project=project)
        self.ecb_exchange_rates_destination = "raw.ecb_exchange_rates"

    def load_table_from_json(
        self,
        data: list[dict],
        destination: str,
        job_config: bigquery.job.load.LoadJobConfig,
    ):
        """
        Load data from a list of dictionaries into a BigQuery table.

        Args:
            data (list[dict]): The data to load as a list of dictionaries.
            destination (str): The destination table in BigQuery.
            job_config (bigquery.job.load.LoadJobConfig): Job configuration for the load operation.
        """
        load_job = self.client.load_table_from_json(
            data, destination, job_config=job_config
        )
        load_job.result()

    def load_ecb_exchange_rates(self, ecb_exchange_rates: list[model.EcbExchangeRate]):
        """
        Load ECB exchange rates into BigQuery table indicated by attribute ecb_exchange_rates_destination.

        Args:
            ecb_exchange_rates (List[model.EcbExchangeRate]): List of EcbExchangeRate instances to be loaded
                into BigQuery.
        """

        dictify = [ecb_rate.to_dict() for ecb_rate in ecb_exchange_rates]
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        self.load_table_from_json(dictify, self.ecb_exchange_rates_destination, job_config)
