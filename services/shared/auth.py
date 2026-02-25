import base64
import hashlib
import hmac
import json
import time

# --- Helpers ----------------------------------------------------------

def _b64url_encode(data: bytes) -> str:
    # Produce URL-safe base64 without padding.
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64url_decode(data: str) -> bytes:
    # Decode URL-safe base64 with padding restoration.
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def encode_token(payload: dict, secret: str, ttl_seconds: int = 3600) -> str:
    # Create a signed JWT using HS256.
    header = {"alg": "HS256", "typ": "JWT"}
    issued_at = int(time.time())
    payload = dict(payload)
    payload["iat"] = issued_at
    payload["exp"] = issued_at + ttl_seconds
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_token(token: str, secret: str) -> dict:
    # Verify a JWT signature and expiration.
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token")
    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_sig, _b64url_decode(sig_b64)):
        raise ValueError("Invalid signature")
    payload = json.loads(_b64url_decode(payload_b64))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("Token expired")
    return payload
