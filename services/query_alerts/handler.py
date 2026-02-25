from shared.aws import resource
from shared.config import ALERTS_TABLE, PATIENTS_TABLE
from shared.response import response

# --- Helpers ----------------------------------------------------------

def _normalize_patient_id(value: object) -> str | None:
    # Normalize DynamoDB attribute values into a plain patient id.
    if value is None:
        return None
    if isinstance(value, dict):
        if "S" in value:
            return value["S"] or None
        if "N" in value:
            return value["N"] or None
    patient_id = str(value).strip()
    return patient_id or None


def _sort_alerts(items: list[dict]) -> list[dict]:
    # Sort alerts by created_at descending.
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)


def _fetch_patient(patient_id: str) -> dict:
    # Load a single patient record from DynamoDB.
    table = resource("dynamodb").Table(PATIENTS_TABLE)
    result = table.get_item(Key={"patient_id": patient_id})
    return result.get("Item", {})


def _attach_patient_login(alerts: list[dict]) -> list[dict]:
    # Merge patient login into alerts for display.
    for alert in alerts:
        patient_id = _normalize_patient_id(alert.get("patient_id"))
        if not patient_id:
            continue
        alert["patient_id"] = patient_id
        if alert.get("patient_login"):
            continue
        patient = _fetch_patient(patient_id)
        if not patient:
            continue
        alert["patient_login"] = patient.get("patient_login", "")
    return alerts


# --- Handler ----------------------------------------------------------

def lambda_handler(event: dict, context: dict) -> dict:
    # Return the alert read model for clinicians.
    table = resource("dynamodb").Table(ALERTS_TABLE)
    result = table.scan()
    items = _sort_alerts(result.get("Items", []))
    items = _attach_patient_login(items)
    return response(200, {"alerts": items})
