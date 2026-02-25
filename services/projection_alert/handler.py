import json

from shared.aws import resource
from shared.config import ALERTS_TABLE

# --- Handler ----------------------------------------------------------

def lambda_handler(event: dict, context: dict) -> dict:
    # Project AlertCreated events into the read model.
    detail = event.get("detail")
    if isinstance(detail, str):
        detail = json.loads(detail)
    if detail.get("type") != "AlertCreated":
        return {"status": "ignored"}
    payload = detail.get("payload", {})
    table = resource("dynamodb").Table(ALERTS_TABLE)
    table.put_item(
        Item={
            "alert_id": payload.get("alert_id"),
            "patient_id": payload.get("patient_id"),
            "patient_login": payload.get("patient_login"),
            "score": payload.get("score"),
            "message": payload.get("message"),
            "created_at": detail.get("timestamp"),
        }
    )
    return {"status": "ok"}
