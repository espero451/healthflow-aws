import json
from uuid import uuid4

from shared.auth import encode_token
from shared.aws import resource
from shared.config import JWT_SECRET, USERS_TABLE
from shared.events import build_event, emit_event
from shared.request import parse_body
from shared.response import response

# --- Helpers ----------------------------------------------------------


def _get_user(username: str) -> dict | None:
    # Load a user record from DynamoDB.
    table = resource("dynamodb").Table(USERS_TABLE)
    result = table.get_item(Key={"username": username})
    return result.get("Item")


def _put_user(username: str, role: str, password: str, patient_id: str | None) -> None:
    # Store a user record in DynamoDB.
    table = resource("dynamodb").Table(USERS_TABLE)
    item = {
        "username": username,
        "role": role,
        "password": password,
    }
    if patient_id:
        item["patient_id"] = patient_id
    table.put_item(Item=item)


def _update_patient(username: str, patient_id: str) -> None:
    # Attach a patient_id to an existing user.
    table = resource("dynamodb").Table(USERS_TABLE)
    table.update_item(
        Key={"username": username},
        UpdateExpression="SET patient_id = :pid",
        ExpressionAttributeValues={":pid": patient_id},
    )


def _emit_patient_created(patient_id: str, username: str) -> None:
    # Emit a PatientCreated event for a new patient.
    event = build_event(
        "PatientCreated",
        {
            "patient_id": patient_id,
            "patient_login": username,
            "email": f"{username}@demo.local",
        },
    )
    emit_event(event)


# --- Handler ----------------------------------------------------------


def lambda_handler(event: dict, context: dict) -> dict:
    # print("START")
    # print("EVENT:", event)  
    # print("BODY RAW:", event.get("body"))

    # Handle login and optional patient registration.
    payload = parse_body(event)
    # print("PARSED")
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    role = str(payload.get("role", "")).strip()
    if not username or not password or role not in {"patient", "clinician"}:
        return response(400, {"detail": "Invalid login data"})
    # print("BEFORE GET USER")
    user = _get_user(username)
    # print("AFTER GET USER")
    if user:
        if user.get("password") != password or user.get("role") != role:
            return response(401, {"detail": "Invalid credentials"})
        patient_id = user.get("patient_id")
        if role == "patient" and not patient_id:
            patient_id = str(uuid4())
            _update_patient(username, patient_id)
            _emit_patient_created(patient_id, username)
        token = encode_token({"sub": username, "role": role}, JWT_SECRET)
        result = {"token": token, "role": role, "new_user": False}
        if role == "patient":
            result["patient_id"] = patient_id
        return response(200, result)

    if role != "patient":
        return response(401, {"detail": "User not found"})

    patient_id = str(uuid4())
    _put_user(username, role, password, patient_id)
    _emit_patient_created(patient_id, username)
    token = encode_token({"sub": username, "role": role}, JWT_SECRET)
    return response(200, {"token": token, "role": role, "patient_id": patient_id, "new_user": True})
