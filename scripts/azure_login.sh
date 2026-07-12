#!/usr/bin/env bash
# Login vía Service Principal usando variables de entorno.
# Uso local: exporta las 4 variables y ejecuta ./scripts/azure_login.sh
set -euo pipefail

: "${AZURE_CLIENT_ID:?Falta AZURE_CLIENT_ID}"
: "${AZURE_CLIENT_SECRET:?Falta AZURE_CLIENT_SECRET}"
: "${AZURE_TENANT_ID:?Falta AZURE_TENANT_ID}"
: "${AZURE_SUBSCRIPTION_ID:?Falta AZURE_SUBSCRIPTION_ID}"

az login --service-principal \
  -u "$AZURE_CLIENT_ID" \
  -p "$AZURE_CLIENT_SECRET" \
  --tenant "$AZURE_TENANT_ID" > /dev/null

az account set --subscription "$AZURE_SUBSCRIPTION_ID"
echo "Autenticado en la suscripción: $AZURE_SUBSCRIPTION_ID"
