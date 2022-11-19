from ecb_exchange_rates import *


def func_entry_point(event, context):
    """
    Entry point to the Python solution for the GCP Function Execution.
    This function calls to ECB Api for as many days back as indicated on attribute days_to_register. Then transform the
    response into a dataframe that is use as vector to populate the data into table bce.EuroaRatio at destination
    database. Configuration and credential for database are indicated by environment variables.

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

    try:
        days_to_register = int(event['attributes']['days_to_register'])
        print("Calling to ECB Api")
        response = call_to_ecb_api_exchange_rate(days_to_register)

        print("Transforming response from ECB Api")
        exchange_df = from_xml_to_dataframe(response.text)

        print("Loading data to database")
        load_to_database_eur_exchange_rate(exchange_df)

        print("Process completed successfully")

    except Exception as e:
        print("Next error has occurred: %s" % e.__str__())
