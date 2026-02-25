import json

from shared.aws import resource
from shared.config import PATIENTS_TABLE

# --- Handler ----------------------------------------------------------

def lambda_handler(event: dict, context: dict) -> dict:
    # Project PatientCreated events into the read model.
    detail = event.get("detail")
    if isinstance(detail, str):
        detail = json.loads(detail)
    if detail.get("type") != "PatientCreated":
        return {"status": "ignored"}
    payload = detail.get("payload", {})
    table = resource("dynamodb").Table(PATIENTS_TABLE)
    table.put_item(
        Item={
            "patient_id": payload.get("patient_id"),
            "patient_login": payload.get("patient_login"),
            "full_name": payload.get("full_name", payload.get("patient_login")),
            "email": payload.get("email", ""),
            "created_at": detail.get("timestamp"),
        }
    )
    return {"status": "ok"}
