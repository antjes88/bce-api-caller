from cloud_function import services
from cloud_function import model
import os


def test_source_ecb_rates(repository_with_ecb_rates, fake_ecb_api):
    """
    GIVEN a fake ecb api
    WHEN we call the service source_ecb_rates()
    THEN the fake data sourced from the fake api should be loaded into the data repository
    """
    fake_ecb_api_caller, expected_ecb_rates, currencies = fake_ecb_api
    bq_repository, ECB_RATES = repository_with_ecb_rates
    services.source_ecb_exchange_rates(bq_repository, currencies, fake_ecb_api_caller)

    expected_ecb_rates = expected_ecb_rates + ECB_RATES

    query_job = bq_repository.client.query(f"SELECT * FROM {os.environ['DATASET']}.{os.environ['DESTINATION_TABLE']}")
    rows = query_job.result()
    results_ecb_rates = []
    for row in rows:
        results_ecb_rates.append(
            model.EcbExchangeRate(
                row.date, row.exchange_rate, row.currency, row.creation_date
            )
        )

    assert len(expected_ecb_rates) == len(results_ecb_rates)
    for ecb_rate in expected_ecb_rates:
        assert ecb_rate in results_ecb_rates
