from src import source_repository, destination_repository


def source_ecb_exchange_rates(
    destination_repository: destination_repository.DestinationAbstractRepository,
    currencies: list[str],
    source_repository: source_repository.SourceAbstractRepository,
):
    """
    Fetches ECB rates from source repository and loads them into destination repository.

    Args:
        destination_repository (destination_repository.DestinationAbstractRepository):
            The data repository to load ECB rates into.
        currencies (List[str]):
            List of currency codes for which to fetch ECB rates.
        source_repository (source_repository.SourceAbstractRepository):
            The data repository to get ECB rates from.
    """
    ecb_rates = source_repository.get_ecb_rates(currencies)
    destination_repository.load_ecb_exchange_rates(ecb_rates)
