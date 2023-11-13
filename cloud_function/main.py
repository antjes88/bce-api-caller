import model
import repository
import services


def function_entry_point(event, context):
    """
    Entry point function for ingesting ECB exchange rates into raw layer of the DW in BigQuery.
    This function initializes a BigQueryRepository and an EcbApiCaller, then calls a service to fetch and load ECB
    rates into BigQuery.

    Args:
         event: The dictionary with data specific to this type of event. The `@type` field maps to
                `type.googleapis.com/google.pubsub.v1.PubsubMessage`. The `data` field maps to the PubsubMessage data
                in a base64-encoded string. The `attributes` field maps to the PubsubMessage attributes
                if any is present.
         context: Metadata of triggering event including `event_id` which maps to the PubsubMessage
                  messageId, `timestamp` which maps to the PubsubMessage publishTime, `event_type` which maps to
                  `google.pubsub.topic.publish`, and `resource` which is a dictionary that describes the service
                  API endpoint pubsub.googleapis.com, the triggering topic's name, and the triggering event type
                  `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
    Returns:
        None
    """
    bq_repository = repository.BiqQueryRepository()
    ecb_api_caller = model.EcbApiCaller(10)
    services.source_ecb_exchange_rates(bq_repository, ["GBP", "USD"], ecb_api_caller)
