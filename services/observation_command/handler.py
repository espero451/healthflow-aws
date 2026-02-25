from uuid import uuid4

from shared.events import build_event, emit_event
from shared.request import parse_body
from shared.response import response


# --- Handler ----------------------------------------------------------

def lambda_handler(event: dict, context: dict) -> dict:
    # Create an ObservationSubmitted event from the API request.
    payload = parse_body(event)
    patient_id = str(payload.get("patient_id", "")).strip()
    try:
        score = int(payload.get("score"))
    except (TypeError, ValueError):
        return response(400, {"detail": "Invalid score"})
    if not patient_id or score < 1 or score > 10:
        return response(400, {"detail": "Invalid observation"})

    patient_login = event.get("requestContext", {}).get("authorizer", {}).get("username", "")
    observation_id = str(uuid4())
    event_payload = {
        "observation_id": observation_id,
        "patient_id": patient_id,
        "patient_login": patient_login,
        "score": score,
    }
    event = build_event("ObservationSubmitted", event_payload)
    emit_event(event)
    return response(200, {"observation_id": observation_id, "event_id": event["event_id"]})
