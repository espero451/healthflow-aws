from shared.auth import decode_token
from shared.config import JWT_SECRET

# --- Helpers ----------------------------------------------------------

def _policy(principal_id: str, effect: str, resource: str, context: dict | None = None) -> dict:
    # Build an IAM policy for API Gateway.
    statement = {
        "Action": "execute-api:Invoke",
        "Effect": effect,
        "Resource": resource,
    }
    return {
        "principalId": principal_id,
        "policyDocument": {"Version": "2012-10-17", "Statement": [statement]},
        "context": context or {},
    }


# --- Handler ----------------------------------------------------------

def lambda_handler(event: dict, context: dict) -> dict:
    # Validate Bearer token and return an auth policy.
    token = event.get("authorizationToken") or ""
    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token, JWT_SECRET)
    except ValueError:
        return _policy("anonymous", "Deny", event.get("methodArn", "*"))
    return _policy(
        payload.get("sub", "user"),
        "Allow",
        event.get("methodArn", "*"),
        {"username": payload.get("sub", ""), "role": payload.get("role", "")},
    )
