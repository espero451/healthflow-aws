import base64
import json

# --- Helpers ----------------------------------------------------------

def parse_body(event: dict) -> dict:
    # Parse JSON request bodies from API Gateway events.
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}
