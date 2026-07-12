#!/usr/bin/env bash
# Aplica la infraestructura de prueba y exporta las variables de entorno
# que consumen los tests de integración.
set -euo pipefail

cd "$(dirname "$0")/../terraform"

terraform init -input=false
terraform apply -input=false -auto-approve

export RESOURCE_GROUP_NAME
export STORAGE_ACCOUNT_NAME
export APP_SERVICE_NAME

RESOURCE_GROUP_NAME=$(terraform output -raw resource_group_name)
STORAGE_ACCOUNT_NAME=$(terraform output -raw storage_account_name)
APP_SERVICE_NAME=$(terraform output -raw app_service_name)

echo "RESOURCE_GROUP_NAME=$RESOURCE_GROUP_NAME"
echo "STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT_NAME"
echo "APP_SERVICE_NAME=$APP_SERVICE_NAME"
echo ""
echo "Exporta estas variables antes de correr 'pytest tests/integration', ej:"
echo "  export RESOURCE_GROUP_NAME STORAGE_ACCOUNT_NAME APP_SERVICE_NAME"
