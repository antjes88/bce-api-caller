import model
import repository


def source_ecb_exchange_rates(
        repo: repository.AbstractRepository, currencies: list[str], ecb_api_caller: model.EcbApiCaller
):
    """
    Fetches ECB rates using an Ecb Api and loads them into a data repository.

    Args:
        repo (repository.AbstractRepository): The data repository to load ECB rates into.
        currencies (List[str]): List of currency codes for which to fetch ECB rates.
        ecb_api_caller (model.EcbApiCaller): The EcbApiCaller instance to use for fetching rates.
    """
    ecb_rates = ecb_api_caller.get_ecb_rates(currencies)
    repo.load_ecb_exchange_rates(ecb_rates)
