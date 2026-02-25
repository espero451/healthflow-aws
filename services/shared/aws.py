import os
from typing import Any
from urllib.parse import urlparse, urlunparse

import boto3


# --- Configuration ----------------------------------------------------

def _endpoint_url() -> str | None:
    # Prefer explicit endpoint override for local runs.
    endpoint = os.getenv("AWS_ENDPOINT_URL")
    if endpoint:
        return _rewrite_localstack_endpoint(endpoint)
    localstack = os.getenv("LOCALSTACK_HOSTNAME")
    if localstack:
        return f"http://{localstack}:4566"
    return None


# --- Helpers ----------------------------------------------------------

def _rewrite_localstack_endpoint(endpoint: str) -> str:
    # Use LocalStack hostname from within Lambda containers.
    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return endpoint
    parsed = urlparse(endpoint)
    if parsed.hostname not in {"localhost", "127.0.0.1"}:
        return endpoint
    host = os.getenv("LOCALSTACK_HOSTNAME", "localstack")
    netloc = f"{host}:{parsed.port}" if parsed.port else host
    return urlunparse(parsed._replace(netloc=netloc))


def client(service: str) -> Any:
    # Build a boto3 client with optional local endpoint.
    endpoint_url = _endpoint_url()
    if endpoint_url:
        return boto3.client(service, endpoint_url=endpoint_url)
    return boto3.client(service)


def resource(service: str) -> Any:
    # Build a boto3 resource with optional local endpoint.
    endpoint_url = _endpoint_url()
    if endpoint_url:
        return boto3.resource(service, endpoint_url=endpoint_url)
    return boto3.resource(service)
