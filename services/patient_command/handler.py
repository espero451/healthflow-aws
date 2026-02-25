from uuid import uuid4

from shared.events import build_event, emit_event
from shared.request import parse_body
from shared.response import response

# --- Handler ----------------------------------------------------------

def lambda_handler(event: dict, context: dict) -> dict:
    # Create a PatientCreated event from the API request.
    payload = parse_body(event)
    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).strip()
    patient_login = str(payload.get("patient_login", "")).strip()
    if not patient_login:
        patient_login = event.get("requestContext", {}).get("authorizer", {}).get("username", "")
    if not full_name:
        full_name = patient_login
    if not email:
        email = f"{patient_login}@demo.local"
    if not patient_login:
        return response(400, {"detail": "Missing patient login"})

    patient_id = str(uuid4())
    event_payload = {
        "patient_id": patient_id,
        "patient_login": patient_login,
        "full_name": full_name,
        "email": email,
    }
    event = build_event("PatientCreated", event_payload)
    emit_event(event)
    return response(200, {"patient_id": patient_id, "event_id": event["event_id"]})
