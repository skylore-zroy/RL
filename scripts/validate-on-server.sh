#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "${project_root}"

bash scripts/server-preflight.sh
docker compose --profile isaac build isaac-validate
docker compose --profile isaac run --rm isaac-validate

test -s validation_results/isaac_model_report.json
echo "isaac_report=${project_root}/validation_results/isaac_model_report.json"