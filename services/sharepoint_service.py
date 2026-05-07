import base64
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests


class SharePointService:
    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

    def download_file(self, file_url, output_dir):
        self._validate_config()

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            token = self._get_access_token()
            share_id = self._build_share_id(file_url)
            metadata = self._get_drive_item_metadata(share_id, token)
        except requests.RequestException as exc:
            raise RuntimeError(
                "No se pudo autenticar o leer el archivo desde SharePoint. "
                "Revisa MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET y permisos "
                "de Microsoft Graph para leer archivos."
            ) from exc

        file_name = metadata.get("name") or self._file_name_from_url(file_url)
        destination = output_dir / self._safe_file_name(file_name)

        try:
            response = requests.get(
                f"{self.GRAPH_BASE_URL}/shares/{share_id}/driveItem/content",
                headers={"Authorization": f"Bearer {token}"},
                timeout=120,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"No se pudo descargar el archivo desde SharePoint: {file_url}"
            ) from exc

        destination.write_bytes(response.content)
        return destination

    def _validate_config(self):
        missing = [
            name
            for name, value in {
                "MS_TENANT_ID": self.tenant_id,
                "MS_CLIENT_ID": self.client_id,
                "MS_CLIENT_SECRET": self.client_secret,
            }.items()
            if not value
        ]

        if missing:
            raise RuntimeError(
                "Faltan variables de SharePoint en .env: " + ", ".join(missing)
            )

    def _get_access_token(self):
        response = requests.post(
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials",
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _get_drive_item_metadata(self, share_id, token):
        response = requests.get(
            f"{self.GRAPH_BASE_URL}/shares/{share_id}/driveItem",
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def _build_share_id(self, file_url):
        encoded = base64.urlsafe_b64encode(file_url.encode("utf-8")).decode("utf-8")
        return "u!" + encoded.rstrip("=")

    def _file_name_from_url(self, file_url):
        path = unquote(urlparse(file_url).path)
        return Path(path).name or "sharepoint_file"

    def _safe_file_name(self, file_name):
        return re.sub(r'[<>:"/\\|?*]', "_", file_name).strip() or "sharepoint_file"
