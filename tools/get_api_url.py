import json
import os
import subprocess

# --- Configuration ----------------------------------------------------

def _endpoint_url() -> str:
    # Return the LocalStack endpoint for API Gateway.
    return os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")


def _awslocal_env() -> dict:
    # Ensure awslocal targets the desired LocalStack endpoint.
    env = os.environ.copy()
    if "LOCALSTACK_ENDPOINT" not in env:
        env["LOCALSTACK_ENDPOINT"] = _endpoint_url()
    return env


def _run_awslocal(args: list[str]) -> dict:
    # Run awslocal and parse the JSON output.
    result = subprocess.run(
        ["awslocal", *args],
        check=True,
        capture_output=True,
        text=True,
        env=_awslocal_env(),
    )
    return json.loads(result.stdout)


# --- Handler ----------------------------------------------------------

def main() -> None:
    # Print the API Gateway invoke URL for LocalStack.
    api_name = os.getenv("API_NAME", "healthflow-api")
    stage = os.getenv("API_STAGE", "local")
    payload = _run_awslocal(["apigateway", "get-rest-apis"])
    apis = payload.get("items", [])
    match = next((api for api in apis if api.get("name") == api_name), None)
    if not match:
        raise SystemExit("API not found. Deploy the CDK stack first.")
    api_id = match["id"]
    base = _endpoint_url()
    print(f"{base}/restapis/{api_id}/{stage}/_user_request_")


if __name__ == "__main__":
    main()
