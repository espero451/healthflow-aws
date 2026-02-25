import json
from decimal import Decimal

# --- Helpers ----------------------------------------------------------

def _json_default(value: object) -> float | int:
    # Serialize Decimal values for JSON output.
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)
    raise TypeError(f"Unsupported type: {type(value)}")


def response(status_code: int, payload: dict) -> dict:
    # Build a JSON API Gateway response.
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        },
        "body": json.dumps(payload, default=_json_default),
    }
