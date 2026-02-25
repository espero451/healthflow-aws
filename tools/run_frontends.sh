#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
API_URL="$(python3 "${SCRIPT_DIR}/get_api_url.py")"

if [[ -z "${API_URL}" ]]; then
  echo "API URL not found. Deploy the CDK stack first."
  exit 1
fi

export VITE_API_BASE_URL="${API_URL}"
echo "Using API URL: ${VITE_API_BASE_URL}"

(
  cd "${ROOT_DIR}/frontend/patient"
  npm run dev
) &
PATIENT_PID=$!

(
  cd "${ROOT_DIR}/frontend/clinician"
  npm run dev
) &
CLINICIAN_PID=$!

cleanup() {
  kill "${PATIENT_PID}" "${CLINICIAN_PID}" 2>/dev/null || true
  wait "${PATIENT_PID}" "${CLINICIAN_PID}" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

wait
