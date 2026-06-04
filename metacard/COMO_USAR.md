# MetaKart — Gerador de Ranking Semanal

## Instalação (só na primeira vez)

### Pré-requisitos
- Python 3.10 ou superior → python.org/downloads
- Tesseract OCR (para o PDF escaneado do Campo Grande)
  - **Mac:** `brew install tesseract tesseract-lang`
  - **Windows:** baixar instalador em github.com/UB-Mannheim/tesseract/wiki

### Instalar dependências
Abra o terminal na pasta `metacard/` e rode:
```
pip install -r requirements.txt
```

---

## Uso semanal

1. Abra o terminal na pasta `metacard/`
2. Rode:
   ```
   streamlit run app.py
   ```
3. O navegador abre automaticamente em `http://localhost:8501`
4. Envie os 3 PDFs do Laptime (Barra, Norte, Campo Grande)
5. Clique em **Gerar Ranking**
6. Baixe o ZIP com as 24 imagens prontas

---

## Estrutura das imagens geradas

```
metacart_ranking_XXXXXXXX.zip
├── Instagram (1080×1350)/
│   ├── barra/
│   │   ├── 01_capa.png
│   │   ├── 02_até_75kg.png
│   │   ├── 03_de_75kg_a_90kg.png
│   │   └── 04_acima_90kg.png
│   ├── norte/       (mesmo formato)
│   └── campo_grande/(mesmo formato)
└── TV (1920×1080)/
    ├── barra/
    ├── norte/
    └── campo_grande/
```

---

## Linha de comando (alternativa ao app web)

```bash
python generate_ranking.py \
  --barra barra.pdf \
  --norte norte.pdf \
  --campo-grande campo_grande.pdf \
  --period "25/05/2026 a 31/05/2026"
```
