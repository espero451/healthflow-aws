import json
from uuid import uuid4

from shared.config import ALERT_THRESHOLD
from shared.events import build_event, emit_event

# --- Helpers ----------------------------------------------------------


def _extract_event(message_body: str) -> dict:
    # Parse EventBridge payloads arriving via SQS.
    try:
        payload = json.loads(message_body)
    except json.JSONDecodeError:
        return {}
    detail = payload.get("detail")
    if isinstance(detail, str):
        try:
            return json.loads(detail)
        except json.JSONDecodeError:
            return {}
    return detail or {}


# --- Handler ----------------------------------------------------------


def lambda_handler(event: dict, context: dict) -> dict:
    # Evaluate observations and emit alerts when threshold is exceeded.
    records = event.get("Records", [])
    for record in records:
        detail = _extract_event(record.get("body", ""))
        if detail.get("type") != "ObservationSubmitted":
            continue
        payload = detail.get("payload", {})
        score = int(payload.get("score", 0))
        if score <= ALERT_THRESHOLD:
            continue
        alert_payload = {
            "alert_id": str(uuid4()),
            "patient_id": payload.get("patient_id"),
            "patient_login": payload.get("patient_login"),
            "score": score,
            "message": f"Score above threshold ({ALERT_THRESHOLD})",
        }
        alert_event = build_event("AlertCreated", alert_payload)
        emit_event(alert_event)
    return {"status": "ok"}
