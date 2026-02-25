#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

LOCALSTACK_ENDPOINT="${LOCALSTACK_ENDPOINT:-http://localhost:4566}"

log() {
  echo "[dev] $*"
}

start_docker() {
  # Start LocalStack containers without touching volumes.
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
  # Seed demo data after a deploy or reset.
  cd "${SCRIPT_DIR}"
  python3 seed_clinician.py
}

# cmd_deploy() {
  # Wipe LocalStack data, deploy infra, then seed and start frontends.
  cd "${ROOT_DIR}"
  docker compose down -v
  sudo rm -rf "${ROOT_DIR}/localstack"
  start_docker
  deploy_infra
  seed_clinician
  start_frontends
# }

cleanup() {
  echo "Bye!.."
  cd "${ROOT_DIR}"
  docker compose stop
}

trap cleanup SIGINT

usage() {
  cat <<EOF
Usage: ./dev.sh <command>

Commands:
  deploy  Deploy, seed data and run frontends
EOF
}

# case "${1:-}" in
#   deploy) cmd_deploy ;;
#   *) usage; exit 1 ;;
# esac
