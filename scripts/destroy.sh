#!/usr/bin/env bash
# Destruye toda la infraestructura de prueba creada por deploy.sh.
set -euo pipefail

cd "$(dirname "$0")/../terraform"

terraform destroy -input=false -auto-approve
