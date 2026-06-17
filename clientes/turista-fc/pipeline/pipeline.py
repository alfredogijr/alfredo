"""
Orquestrador principal do pipeline diário de stories do Turista FC.
Disparado pelo cron / GitHub Actions todo dia às 7h.

Fluxo:
  1. Coletor  — manchetes RSS do dia
  2. Curador  — seleciona e escreve 5 stories via Anthropic API
  3. Renderer — gera 5 PNGs 1080x1920
  4. Uploader — sobe PNGs no Google Drive e obtém URLs públicas
  5. Publisher — agenda no Metricool para publicar às 8h
"""
from __future__ import annotations

import sys
import traceback

from collector import collect
from curator   import curate
from renderer  import render_all
from uploader  import upload_images
from publisher import schedule_stories


def run():
    print("=" * 50)
    print("PIPELINE TURISTA FC — iniciando")
    print("=" * 50)

    # 1. Coletar
    print("\n[1/5] Coletando manchetes...")
    headlines = collect()
    if not headlines:
        print("AVISO: nenhuma manchete coletada. Abortando.")
        sys.exit(1)

    # 2. Curar
    print("\n[2/5] Curando com Anthropic...")
    stories = curate(headlines)

    # 3. Renderizar
    print("\n[3/5] Renderizando stories...")
    paths = render_all(stories)

    # 4. Upload
    print("\n[4/5] Subindo para o Google Drive...")
    urls = upload_images(paths)

    # 5. Publicar
    print("\n[5/5] Agendando no Metricool...")
    results = schedule_stories(urls)

    print("\n" + "=" * 50)
    agendados = sum(1 for r in results if "error" not in r)
    print(f"PIPELINE CONCLUIDO — {agendados}/5 stories agendados")
    print("=" * 50)

    if agendados < 5:
        sys.exit(1)


if __name__ == "__main__":
    try:
        run()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
