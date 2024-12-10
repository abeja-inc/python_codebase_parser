import google_crc32c
from google.cloud import secretmanager


def get_secret_on_google_cloud(project_id: str, secret_name: str, secret_ver: str) -> str:
    """
    Retrieve information from the Secret Manager by specifying the project ID, secret name, and secret version.

    Parameters
    ----------
    project_id : str
        The project ID.
    secret_name : str
        The secret name.
    secret_ver : str
        The secret version.

    Returns
    -------
    str
        The secret data.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_name, secret_ver)
    response = client.access_secret_version(request={"name": name})

    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        return response

    return response.payload.data.decode("UTF-8")
