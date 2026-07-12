"""
Pruebas de conectividad/API: validan que se pueda hablar con los servicios
de Azure usando el Azure SDK, más allá de que los recursos existan.
Incluye: autenticación, listado de recursos por suscripción, y una
operación de escritura/lectura real contra Blob Storage y un healthcheck
HTTP contra la Web App desplegada.
"""

import requests
import pytest


@pytest.fixture(scope="module")
def resource_client(azure_credential, subscription_id):
    pytest.importorskip("azure.mgmt.resource")
    from azure.mgmt.resource import ResourceManagementClient

    return ResourceManagementClient(azure_credential, subscription_id)


@pytest.fixture(scope="module")
def blob_service_client(azure_credential, storage_account_name):
    pytest.importorskip("azure.storage.blob")
    from azure.storage.blob import BlobServiceClient

    account_url = f"https://{storage_account_name}.blob.core.windows.net"
    return BlobServiceClient(account_url=account_url, credential=azure_credential)


def test_authentication_succeeds(azure_credential):
    """Confirma que el ClientSecretCredential obtiene un token válido."""
    token = azure_credential.get_token("https://management.azure.com/.default")
    assert token.token
    assert token.expires_on > 0


def test_can_list_resources_in_subscription(resource_client):
    """Verifica que las credenciales tienen permiso de lectura sobre la
    suscripción (RBAC correcto)."""
    resources = resource_client.resources.list()
    # Basta con poder iterar sin excepción de autorización.
    _ = next(iter(resources), None)


def test_can_write_and_read_blob(blob_service_client):
    """Prueba de extremo a extremo sobre Blob Storage: sube un blob de
    prueba y lo vuelve a leer para confirmar conectividad real de datos
    (no solo del plano de control/ARM)."""
    container_client = blob_service_client.get_container_client("testdata")
    blob_name = "jenkins-connectivity-check.txt"
    content = b"jenkins-azure-testing connectivity check"

    container_client.upload_blob(name=blob_name, data=content, overwrite=True)
    downloaded = container_client.download_blob(blob_name).readall()

    assert downloaded == content

    container_client.delete_blob(blob_name)


def test_web_app_responds_over_https(app_service_name):
    """Healthcheck HTTP simple contra la Web App recién desplegada."""
    url = f"https://{app_service_name}.azurewebsites.net"
    try:
        response = requests.get(url, timeout=30)
    except requests.exceptions.RequestException as exc:
        pytest.fail(f"No se pudo conectar a {url}: {exc}")

    # Una app recién creada sin código propio típicamente responde 200
    # (página por defecto) — solo confirmamos que el servicio responde.
    assert response.status_code < 500
