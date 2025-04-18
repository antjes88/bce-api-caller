from src import source_repository, destination_repository, model


def source_exchange_rates(
    destination_repository: destination_repository.AbstractDestinationRepository,
    currency_pairs: list[model.CurrencyPair],
    source_repository: source_repository.AbstractSourceRepository,
):
    """
    Fetches exchange rates from source repository and loads them into destination repository.

    Args:
        destination_repository (destination_repository.AbstractDestinationRepository):
            The data repository to load exchange rates into.
        currency_pairs (list[model.CurrencyPair]):
            List of currency pairs for which to fetch exchange rates.
        source_repository (source_repository.AbstractSourceRepository):
            The data repository to get exchange rates from.
    """
    exchange_rates = source_repository.get_exchange_rates(currency_pairs)
    destination_repository.load_exchange_rates(exchange_rates)
