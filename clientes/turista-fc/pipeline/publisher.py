"""
Stage 5 — Publicador
Agenda os 5 stories no Metricool para publicação às 8h (America/Sao_Paulo).
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

import httpx

METRICOOL_BRAND_ID = 6404724
METRICOOL_API_BASE = "https://app.metricool.com/api/v2"

# Margem de segurança: 15min após o horário de publicação desejado para evitar
# "data no passado" caso o cron dispare com pequeno atraso.
PUBLISH_HOUR   = 8
PUBLISH_MINUTE = 0
SAFETY_MARGIN_MINUTES = 5


def _get_token() -> str:
    token = os.environ.get("METRICOOL_TOKEN")
    if not token:
        raise EnvironmentError("METRICOOL_TOKEN não definida.")
    return token


def _publication_datetime(index: int) -> str:
    """
    Retorna a data/hora de publicação para o story `index` (1-5).
    Stories são espaçados de 2 minutos para evitar conflitos de fila.
    Formato: YYYY-MM-DDThh:mm:ss
    """
    now = datetime.now()   # horário local do servidor
    # Se já passou das 7h30, publica amanhã
    target = now.replace(hour=PUBLISH_HOUR, minute=PUBLISH_MINUTE + SAFETY_MARGIN_MINUTES,
                         second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    target += timedelta(minutes=2 * (index - 1))
    return target.strftime("%Y-%m-%dT%H:%M:%S")


def schedule_stories(image_urls: list[str]) -> list[dict]:
    """
    Agenda cada URL como um story no Metricool.
    Retorna lista de respostas da API.
    """
    token   = _get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }
    results = []

    for i, url in enumerate(image_urls, start=1):
        pub_dt = _publication_datetime(i)
        payload = {
            "brandId": METRICOOL_BRAND_ID,
            "blogId":  METRICOOL_BRAND_ID,
            "draft":   False,
            "autoPublish": True,
            "providers": ["instagram"],
            "instagramData": {
                "type": "STORY",
                "media": [url],
            },
            "publicationDate": {
                "dateTime": pub_dt,
                "timezone": "America/Sao_Paulo",
            },
        }

        resp = httpx.post(
            f"{METRICOOL_API_BASE}/posts",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if resp.status_code in (200, 201):
            print(f"  [publisher] story {i}/5 agendado para {pub_dt}")
            results.append(resp.json())
        else:
            print(f"  [publisher] ERRO story {i}: {resp.status_code} — {resp.text[:200]}")
            results.append({"error": resp.status_code, "body": resp.text})

    return results


if __name__ == "__main__":
    sample_urls = ["https://example.com/test.png"] * 5
    schedule_stories(sample_urls)
