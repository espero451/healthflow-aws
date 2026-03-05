#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

LOCALSTACK_ENDPOINT="${LOCALSTACK_ENDPOINT:-http://localhost:4566}"

start_docker() {
  cd "${ROOT_DIR}"
  docker compose up -d
}

start_frontends() {
  cd "${SCRIPT_DIR}"
  log "Starting frontends."
  ./run_frontends.sh
}

deploy_infra() {
  # Bootstrap and deploy the CDK stack into LocalStack.
  cd "${ROOT_DIR}/infra"
  npm install
  LOCALSTACK_ENDPOINT="${LOCALSTACK_ENDPOINT}" cdklocal bootstrap
  AWS_S3_FORCE_PATH_STYLE=1 LOCALSTACK_ENDPOINT="${LOCALSTACK_ENDPOINT}" \
    cdklocal deploy --all --require-approval never
}

seed_clinician() {
  # Seed demo data
  cd "${SCRIPT_DIR}"
  python3 seed_clinician.py
}


cd "${ROOT_DIR}"
docker compose down -v
# sudo rm -rf "${ROOT_DIR}/localstack"
start_docker
deploy_infra
seed_clinician
start_frontends

trap cleanup SIGINT
