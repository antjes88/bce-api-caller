import os
import click
from src import source_repository, destination_repository, services
from src.utils.gcp_clients import create_bigquery_client
from src.utils.logs import default_module_logger
from typing import Tuple

logger = default_module_logger(__file__)


@click.command()
@click.option(
    "--currency",
    multiple=True,
    type=str,
    help="You can specify this option multiple times.",
)
def get_ecb_rates(currency: Tuple[str]):
    """
    Fetches exchange rates against the EURO from the ECB (European Central Bank)
    API for the specified currencies and stores them in a BigQuery repository.

    Args:
        currency (Tuple[str]):
            A tuple of currency codes (e.g., ["USD", "GBP"]) for which exchange
            rates are to be fetched.
    """
    currencies = list(currency)
    logger.info(f"Currencies: '{currencies}'.")
    bq_repository = destination_repository.BiqQueryDestinationRepository(
        create_bigquery_client(os.environ["PROJECT"])
    )
    ecb_api_caller = source_repository.EcbApiCaller(10)
    services.source_ecb_exchange_rates(bq_repository, currencies, ecb_api_caller)
