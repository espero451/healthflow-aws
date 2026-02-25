import json

from shared.aws import resource
from shared.config import OBSERVATIONS_TABLE

# --- Handler ----------------------------------------------------------

def lambda_handler(event: dict, context: dict) -> dict:
    # Project ObservationSubmitted events into the read model.
    detail = event.get("detail")
    if isinstance(detail, str):
        detail = json.loads(detail)
    if detail.get("type") != "ObservationSubmitted":
        return {"status": "ignored"}
    payload = detail.get("payload", {})
    table = resource("dynamodb").Table(OBSERVATIONS_TABLE)
    table.put_item(
        Item={
            "observation_id": payload.get("observation_id"),
            "patient_id": payload.get("patient_id"),
            "patient_login": payload.get("patient_login"),
            "score": payload.get("score"),
            "created_at": detail.get("timestamp"),
        }
    )
    return {"status": "ok"}
