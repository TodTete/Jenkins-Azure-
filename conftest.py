"""
Fixtures compartidas de pytest.

Los tests de integración leen la configuración de Azure desde variables de
entorno (las mismas que exporta el Jenkinsfile tras el `terraform apply` y
el `az login`):

    AZURE_SUBSCRIPTION_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_ID
    AZURE_CLIENT_SECRET
    RESOURCE_GROUP_NAME
    STORAGE_ACCOUNT_NAME
    APP_SERVICE_NAME

Si faltan credenciales o variables de recursos, los tests de integración se
saltan automáticamente (skip) en vez de fallar, para que `pytest tests/unit`
y `pytest tests/iac` sigan funcionando sin acceso a Azure.
"""

import os

import pytest


def _env(name: str) -> str | None:
    return os.environ.get(name)


@pytest.fixture(scope="session")
def azure_credential():
    pytest.importorskip("azure.identity")
    from azure.identity import ClientSecretCredential

    required = ["AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"]
    missing = [v for v in required if not _env(v)]
    if missing:
        pytest.skip(f"Faltan variables de entorno para autenticar con Azure: {missing}")

    return ClientSecretCredential(
        tenant_id=_env("AZURE_TENANT_ID"),
        client_id=_env("AZURE_CLIENT_ID"),
        client_secret=_env("AZURE_CLIENT_SECRET"),
    )


@pytest.fixture(scope="session")
def subscription_id():
    sub_id = _env("AZURE_SUBSCRIPTION_ID")
    if not sub_id:
        pytest.skip("AZURE_SUBSCRIPTION_ID no está definido")
    return sub_id


@pytest.fixture(scope="session")
def resource_group_name():
    rg = _env("RESOURCE_GROUP_NAME")
    if not rg:
        pytest.skip("RESOURCE_GROUP_NAME no está definido (¿se ejecutó terraform apply?)")
    return rg


@pytest.fixture(scope="session")
def storage_account_name():
    name = _env("STORAGE_ACCOUNT_NAME")
    if not name:
        pytest.skip("STORAGE_ACCOUNT_NAME no está definido (¿se ejecutó terraform apply?)")
    return name


@pytest.fixture(scope="session")
def app_service_name():
    name = _env("APP_SERVICE_NAME")
    if not name:
        pytest.skip("APP_SERVICE_NAME no está definido (¿se ejecutó terraform apply?)")
    return name
