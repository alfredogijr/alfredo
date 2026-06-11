from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm

def gerar_pdf():
    path = "/home/user/alfredo/alow-barra-checklist-testes.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4

    margin = 2 * cm
    y = h - 2 * cm

    def titulo(text, size=18, cor=colors.HexColor("#1a1a2e")):
        nonlocal y
        c.setFont("Helvetica-Bold", size)
        c.setFillColor(cor)
        c.drawString(margin, y, text)
        y -= size * 0.6

    def linha_h(cor=colors.HexColor("#e0e0e0")):
        nonlocal y
        c.setStrokeColor(cor)
        c.setLineWidth(0.5)
        c.line(margin, y, w - margin, y)
        y -= 0.4 * cm

    def subtitulo(text):
        nonlocal y
        if y < 4 * cm:
            c.showPage()
            y = h - 2 * cm
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#0d47a1"))
        c.drawString(margin, y, text)
        y -= 0.7 * cm

    def item(text):
        nonlocal y
        if y < 3 * cm:
            c.showPage()
            y = h - 2 * cm
        # checkbox
        c.setStrokeColor(colors.HexColor("#555555"))
        c.setLineWidth(1)
        c.rect(margin, y - 0.3 * cm, 0.4 * cm, 0.4 * cm)
        # texto
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(margin + 0.6 * cm, y, text)
        y -= 0.65 * cm

    def espaco(n=0.3):
        nonlocal y
        y -= n * cm

    # ── Cabeçalho ──
    c.setFillColor(colors.HexColor("#0d47a1"))
    c.rect(0, h - 3 * cm, w, 3 * cm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.white)
    c.drawString(margin, h - 1.5 * cm, "Alow Barra — Checklist de Testes")
    c.setFont("Helvetica", 10)
    c.drawString(margin, h - 2.1 * cm, "Squad Dev  |  Versão 1.0  |  Junho 2026")

    y = h - 3.8 * cm

    # ── Seção 1 ──
    subtitulo("1. Resgate de cupom normal")
    item("Abrir um cupom ativo e resgatar")
    item("Confirmar que o código ALOW-XXXXX foi gerado")
    item("Conferir se o redeemed_count subiu +1")
    espaco()

    # ── Seção 2 ──
    subtitulo("2. Bloqueio por CPF")
    item("Resgatar um cupom com CPF limite = 1")
    item("Tentar resgatar o mesmo cupom com o mesmo CPF")
    item("Deve aparecer mensagem de erro bloqueando")
    espaco()

    # ── Seção 3 ──
    subtitulo("3. Cupom esgotado")
    item("Resgatar um cupom até atingir a quantidade máxima")
    item("Confirmar que o status muda para sold_out")
    item("Confirmar que não aparece mais para o consumidor")
    espaco()

    # ── Seção 4 ──
    subtitulo("4. Validação pelo lojista")
    item("Acessar a tela \"Validar Resgate\"")
    item("Digitar um código ALOW-XXXXX válido")
    item("Confirmar os dados do cliente e clicar em \"Confirmar Uso\"")
    item("Checar que o status mudou para used e a data foi registrada")
    espaco()

    # ── Seção 5 ──
    subtitulo("5. Cupom vencido")
    item("Mudar a end_date de um cupom para ontem")
    item("Confirmar que ele sumiu da listagem do consumidor")
    espaco()

    # ── Seção 6 ──
    subtitulo("6. Validação do formulário")
    item("Tentar cadastrar com nome só de números (ex: 12345678900)")
    item("Deve bloquear com mensagem de erro")
    item("Tentar CPF com menos de 11 dígitos — deve bloquear")
    espaco()

    # ── Rodapé ──
    linha_h()
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#888888"))
    c.drawString(margin, y, "Gerado pelo Squad Dev  •  alow-barra-checklist-testes.pdf")
    c.drawRightString(w - margin, y, "Marque cada item conforme testar")

    c.save()
    print(f"PDF gerado: {path}")

gerar_pdf()
