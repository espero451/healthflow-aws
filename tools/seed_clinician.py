import json
import os
import subprocess
from datetime import datetime, timezone
    
    
    # Use:
    # python3 seed_clinician.py
    
    # Result:
    # username: clinician1
    # password: demo

    # Open http://localhost:5174/ and log in


# --- Configuration ----------------------------------------------------

def _endpoint_url() -> str:
    # Return the LocalStack endpoint for DynamoDB.
    return os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")


def _awslocal_env() -> dict:
    # Ensure awslocal targets the desired LocalStack endpoint.
    env = os.environ.copy()
    if "LOCALSTACK_ENDPOINT" not in env:
        env["LOCALSTACK_ENDPOINT"] = _endpoint_url()
    return env


def _run_awslocal(args: list[str]) -> None:
    # Run awslocal for its side effects and surface failures.
    subprocess.run(
        ["awslocal", *args],
        check=True,
        capture_output=True,
        text=True,
        env=_awslocal_env(),
    )


# --- Handler ----------------------------------------------------------


def main() -> None:
    # Seed a clinician user in DynamoDB.
    table_name = os.getenv("USERS_TABLE", "healthflow-users")
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    item = {
        "username": {"S": "clinician1"},
        "role": {"S": "clinician"},
        "password": {"S": "demo"},
        "created_at": {"S": created_at},
    }
    _run_awslocal(
        [
            "dynamodb",
            "put-item",
            "--table-name",
            table_name,
            "--item",
            json.dumps(item),
        ]
    )
    print("Seeded clinician user: clinician1 / demo")


if __name__ == "__main__":
    main()
