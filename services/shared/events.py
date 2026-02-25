import json
from datetime import datetime, timezone
from uuid import uuid4

from shared.aws import client, resource
from shared.config import EVENT_BUS_NAME, EVENTS_TABLE

# --- Event Schema -----------------------------------------------------

EVENT_TYPES = {"PatientCreated", "ObservationSubmitted", "AlertCreated"}


def build_event(event_type: str, payload: dict) -> dict:
    # Build a normalized event envelope.
    if event_type not in EVENT_TYPES:
        raise ValueError("Unsupported event type")
    return {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "type": event_type,
        "payload": payload,
    }


# --- Event Publishing -------------------------------------------------

def store_event(event: dict) -> None:
    # Persist the event into DynamoDB for tracing.
    table = resource("dynamodb").Table(EVENTS_TABLE)
    table.put_item(
        Item={
            "event_id": event["event_id"],
            "timestamp": event["timestamp"],
            "type": event["type"],
            "payload": event["payload"],
        }
    )


def publish_event(event: dict) -> None:
    # Publish the event onto EventBridge.
    events_client = client("events")
    events_client.put_events(
        Entries=[
            {
                "Source": "healthflow",
                "DetailType": event["type"],
                "Detail": json.dumps(event),
                "EventBusName": EVENT_BUS_NAME,
            }
        ]
    )


def emit_event(event: dict) -> None:
    # Store and publish the event.
    store_event(event)
    publish_event(event)
