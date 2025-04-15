from google.cloud import bigquery
from typing import Optional


def create_bigquery_client(project_id: Optional[str] = None) -> bigquery.Client:
    """Creates and returns a Google BigQuery client.

    Args:
        project_id (str, optional): The Google Cloud project ID.
    Returns:
        google.cloud.bigquery.Client: A client for interacting with Google BigQuery.
    """
    return bigquery.Client(project=project_id)
