from src import model
import os


def test_load_ecb_rates(repository_with_ecb_rates):
    """
    GIVEN a repository and a collection of ECB Exchange Rates
    WHEN they are passed as arguments to BiqQueryRepository.load_ecb_exchange_rates()
    THEN ECB Exchange Rates should be loaded into the destination table in the data repository
    """
    bq_repository, ECB_EXCHANGE_RATES = repository_with_ecb_rates
    query_job = bq_repository.client.query(
        f"SELECT * FROM {os.environ['DATASET']}.{os.environ['DESTINATION_TABLE']}"
    )
    rows = query_job.result()
    results_ecb_rates = []
    for row in rows:
        results_ecb_rates.append(
            model.EcbExchangeRate(
                row.date, row.exchange_rate, row.currency, row.creation_date
            )
        )

    assert len(ECB_EXCHANGE_RATES) == len(results_ecb_rates)
    for ecb_rate in ECB_EXCHANGE_RATES:
        assert ecb_rate in results_ecb_rates
