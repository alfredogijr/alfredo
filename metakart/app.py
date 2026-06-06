#!/usr/bin/env python3
"""
MetaKart - Gerador de Ranking Semanal
Interface web para gerar imagens de ranking a partir dos PDFs do Laptime.
"""

import streamlit as st
import zipfile
import io
import os
import tempfile
from pathlib import Path

# Importa a lógica de geração
from generate_ranking import parse_pdf, generate_all, TRACKS, OUT_IG, OUT_TV

# ─── Página ────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="MetaKart · Ranking Semanal",
    page_icon="🏎️",
    layout="centered",
)

# Logo + título
logo_path = Path(__file__).parent / "assets" / "logo_metakart.png"
if logo_path.exists():
    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        st.image(str(logo_path), width=120)
    with col_title:
        st.title("Gerador de Ranking Semanal")
        st.caption("Envie os 3 PDFs do Laptime e baixe as imagens prontas.")
else:
    st.title("🏎️ MetaKart — Ranking Semanal")

st.divider()

# ─── Upload dos PDFs ───────────────────────────────────────────────────────────

st.subheader("1. Envie os PDFs do Laptime")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("🟣 **Barra**")
    st.caption("Shopping Metropolitano")
    barra_file = st.file_uploader(
        "PDF Barra", type="pdf", key="barra", label_visibility="collapsed"
    )

with col2:
    st.markdown("🟢 **Norte**")
    st.caption("Norte Shopping")
    norte_file = st.file_uploader(
        "PDF Norte", type="pdf", key="norte", label_visibility="collapsed"
    )

with col3:
    st.markdown("🟠 **Campo Grande**")
    st.caption("ParkShopping Campo Grande")
    campo_file = st.file_uploader(
        "PDF Campo Grande", type="pdf", key="campo", label_visibility="collapsed"
    )

# ─── Período (opcional) ────────────────────────────────────────────────────────

st.subheader("2. Período (opcional)")
st.caption("Deixe em branco para detectar automaticamente pelas datas dos PDFs.")
period_input = st.text_input(
    "Período",
    placeholder="Ex: 25/05/2026 a 31/05/2026",
    label_visibility="collapsed",
)

# ─── Gerar ─────────────────────────────────────────────────────────────────────

st.subheader("3. Gerar")

all_uploaded = barra_file and norte_file and campo_file

if not all_uploaded:
    missing = []
    if not barra_file:
        missing.append("Barra")
    if not norte_file:
        missing.append("Norte")
    if not campo_file:
        missing.append("Campo Grande")
    st.info(f"Faltam os PDFs: {', '.join(missing)}")

generate_btn = st.button(
    "🏁 Gerar Ranking",
    disabled=not all_uploaded,
    use_container_width=True,
    type="primary",
)

if generate_btn and all_uploaded:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Salva os PDFs enviados em arquivos temporários
        pdf_paths = {}
        for key, uploaded, track_key in [
            ("barra",        barra_file, "barra"),
            ("norte",        norte_file, "norte"),
            ("campo_grande", campo_file, "campo_grande"),
        ]:
            path = tmpdir / f"{key}.pdf"
            path.write_bytes(uploaded.read())
            pdf_paths[track_key] = str(path)

        # Redireciona saída para pasta temporária
        import generate_ranking as gr
        orig_ig = gr.OUT_IG
        orig_tv = gr.OUT_TV
        gr.OUT_IG = tmpdir / "instagram"
        gr.OUT_TV = tmpdir / "tv"

        progress = st.progress(0, text="Lendo PDFs...")
        log_area = st.empty()
        logs = []

        def log(msg):
            logs.append(msg)
            log_area.text("\n".join(logs[-6:]))

        tracks_data = []
        for i, (key, path) in enumerate(pdf_paths.items()):
            nome = TRACKS[key]["name"]
            progress.progress((i + 1) * 15, text=f"Lendo PDF: {nome}…")
            log(f"📄 Lendo {nome}…")
            try:
                track = parse_pdf(path, key)
                n = sum(len(c.entries) for c in track.categories)
                log(f"   ✅ {nome}: {n} entradas, {len(track.categories)} categorias")
                tracks_data.append(track)
            except Exception as e:
                st.error(f"Erro ao ler PDF de {nome}: {e}")
                gr.OUT_IG = orig_ig
                gr.OUT_TV = orig_tv
                st.stop()

        progress.progress(50, text="Gerando imagens…")
        log("🖼️ Gerando imagens…")

        try:
            generate_all(
                tracks_data,
                period_override=period_input.strip() or None,
            )
        except Exception as e:
            st.error(f"Erro ao gerar imagens: {e}")
            gr.OUT_IG = orig_ig
            gr.OUT_TV = orig_tv
            st.stop()

        # Restaura caminhos originais
        gr.OUT_IG = orig_ig
        gr.OUT_TV = orig_tv

        progress.progress(85, text="Empacotando arquivos…")
        log("📦 Criando ZIP…")

        # Cria ZIP com todas as imagens
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for fmt, folder in [("Instagram (1080×1350)", tmpdir / "instagram"),
                                 ("TV (1920×1080)",        tmpdir / "tv")]:
                for img_path in sorted(folder.rglob("*.png")):
                    arcname = f"{fmt}/{img_path.parent.name}/{img_path.name}"
                    zf.write(img_path, arcname)

        progress.progress(100, text="Pronto!")
        log("✅ Concluído!")

        zip_buf.seek(0)
        total_files = sum(1 for _ in (tmpdir / "instagram").rglob("*.png")) * 2

        st.success(f"✅ {total_files} imagens geradas com sucesso!")

        # Determina o período detectado
        if tracks_data and tracks_data[0].period_start:
            periodo_str = (
                f"{tracks_data[0].period_start.replace('/', '')}"
                f"-{tracks_data[0].period_end.replace('/', '')}"
            )
        else:
            periodo_str = "ranking"

        st.download_button(
            label="⬇️ Baixar todas as imagens (ZIP)",
            data=zip_buf,
            file_name=f"metacart_ranking_{periodo_str}.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary",
        )

        # Preview de algumas imagens
        st.subheader("Preview")
        preview_cols = st.columns(3)
        covers = list((tmpdir / "instagram").rglob("01_capa.png"))
        for i, cover in enumerate(sorted(covers)[:3]):
            with preview_cols[i]:
                track_name = cover.parent.name.replace("_", " ").title()
                st.image(str(cover), caption=track_name, use_container_width=True)

# ─── Rodapé ────────────────────────────────────────────────────────────────────

st.divider()
st.caption(
    "MetaKart Indoor Karting · Gerador de Ranking Semanal  \n"
    "Para rodar localmente: `streamlit run app.py`"
)
