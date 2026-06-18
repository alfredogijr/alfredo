"""
Stage 4 — Hospedador
Sobe os PNGs no Google Drive e retorna URLs públicas de download direto.
Requer variáveis de ambiente:
  GOOGLE_SERVICE_ACCOUNT_JSON — conteúdo completo do arquivo .json (não o caminho)
  GOOGLE_DRIVE_FOLDER_ID      — ID da pasta destino no Drive
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials


SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_service():
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON não definida.")
    info = json.loads(sa_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def upload_images(paths: list[Path]) -> list[str]:
    """
    Sobe cada PNG no Google Drive e retorna lista de URLs públicas diretas.
    URL formato: https://drive.google.com/uc?id=FILE_ID&export=download
    """
    service = _get_service()
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
    urls: list[str] = []

    for path in paths:
        meta = {"name": path.name}
        if folder_id:
            meta["parents"] = [folder_id]

        media = MediaFileUpload(str(path), mimetype="image/png", resumable=False)
        file = service.files().create(
            body=meta, media_body=media, fields="id"
        ).execute()
        file_id = file["id"]

        # Tornar público
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()

        url = f"https://drive.google.com/uc?id={file_id}&export=download"
        urls.append(url)
        print(f"  [uploader] {path.name} -> {url}")

    return urls


if __name__ == "__main__":
    from pathlib import Path
    sample = list((Path(__file__).parent / "output").glob("story_*.png"))
    urls = upload_images(sorted(sample))
    for u in urls:
        print(u)
