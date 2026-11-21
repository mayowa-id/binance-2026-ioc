#!/usr/bin/env bash
# Run from the repository root. Compose loads .env; do not source it as shell code.
set -euo pipefail

attempts="${SPLUNK_WAIT_ATTEMPTS:-90}"
if [[ ! "$attempts" =~ ^[1-9][0-9]*$ ]]; then
  echo 'SPLUNK_WAIT_ATTEMPTS must be a positive integer.' >&2
  exit 2
fi

for ((attempt=1; attempt<=attempts; attempt++)); do
  # Credentials stay inside the container, out of host command arguments.
  # -k is limited to the local lab's self-signed management certificate.
  if docker compose exec -T splunk sh -c '
    curl --silent --fail --insecure --connect-timeout 3 --max-time 5 \
      --user "admin:$SPLUNK_PASSWORD" \
      "https://localhost:8089/services/server/info?output_mode=json" >/dev/null
  ' 2>/dev/null; then
    echo 'Splunk management API is ready (authenticated request succeeded).'
    exit 0
  fi
  sleep 5
done

echo 'Timed out waiting for Splunk. Inspect: docker compose ps; docker compose logs splunk' >&2
exit 1
