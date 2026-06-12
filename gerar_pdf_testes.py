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

    def nova_pagina():
        nonlocal y
        c.showPage()
        y = h - 2 * cm

    def check_pagina(min_y=3.5 * cm):
        nonlocal y
        if y < min_y:
            nova_pagina()

    def subtitulo(text):
        nonlocal y
        check_pagina(5 * cm)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#0d47a1"))
        c.drawString(margin, y, text)
        y -= 0.7 * cm

    def item(text):
        nonlocal y
        check_pagina()
        c.setStrokeColor(colors.HexColor("#555555"))
        c.setLineWidth(1)
        c.rect(margin, y - 0.3 * cm, 0.4 * cm, 0.4 * cm)
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(margin + 0.6 * cm, y, text)
        y -= 0.65 * cm

    def espaco(n=0.4):
        nonlocal y
        y -= n * cm

    def rodape():
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#888888"))
        c.drawString(margin, 1.2 * cm, "Gerado pelo Squad Dev  •  alow-barra-checklist-testes.pdf  •  v2.0")
        c.drawRightString(w - margin, 1.2 * cm, "Marque cada item conforme testar")

    # ── Cabeçalho ──
    c.setFillColor(colors.HexColor("#0d47a1"))
    c.rect(0, h - 3 * cm, w, 3 * cm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.white)
    c.drawString(margin, h - 1.5 * cm, "Alow Barra — Checklist de Testes")
    c.setFont("Helvetica", 10)
    c.drawString(margin, h - 2.1 * cm, "Squad Dev  |  Versão 2.0  |  Junho 2026")

    y = h - 3.8 * cm

    # ═══════════════════════════════
    # BLOCO 1 — Fluxo de resgate
    # ═══════════════════════════════
    subtitulo("1. Resgate de cupom normal")
    item("Abrir um cupom ativo e resgatar")
    item("Confirmar que o código ALOW-XXXXX foi gerado")
    item("Conferir se o redeemed_count subiu +1")
    espaco()

    subtitulo("2. Bloqueio por CPF")
    item("Resgatar um cupom com CPF limite = 1")
    item("Tentar resgatar o mesmo cupom com o mesmo CPF")
    item("Deve aparecer mensagem de erro bloqueando")
    espaco()

    subtitulo("3. Cupom esgotado")
    item("Resgatar um cupom até atingir a quantidade máxima")
    item("Confirmar que o status muda para sold_out")
    item("Confirmar que não aparece mais para o consumidor")
    espaco()

    subtitulo("4. Validação pelo lojista")
    item("Acessar a tela \"Validar Resgate\"")
    item("Digitar um código ALOW-XXXXX válido")
    item("Confirmar os dados do cliente e clicar em \"Confirmar Uso\"")
    item("Checar que o status mudou para used e a data foi registrada")
    espaco()

    subtitulo("5. Cupom vencido")
    item("Mudar a end_date de um cupom para ontem")
    item("Confirmar que ele sumiu da listagem do consumidor")
    espaco()

    subtitulo("6. Validação do formulário")
    item("Tentar cadastrar com nome só de números (ex: 12345678900)")
    item("Deve bloquear com mensagem de erro")
    item("Tentar CPF com menos de 11 dígitos — deve bloquear")

    rodape()

    # ═══════════════════════════════
    # PÁGINA 2 — Melhorias de exibição
    # ═══════════════════════════════
    nova_pagina()

    c.setFillColor(colors.HexColor("#0d47a1"))
    c.rect(0, h - 1.6 * cm, w, 1.6 * cm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.white)
    c.drawString(margin, h - 1.1 * cm, "Alow Barra — Checklist de Testes  |  Parte 2: Exibição e UX")

    y = h - 2.5 * cm

    subtitulo("7. Contador de resgates (show_redeemed_count)")
    item("Abrir um cupom que tem show_redeemed_count = true")
    item("Confirmar que o número de resgates aparece na tela")
    item("Abrir um cupom com show_redeemed_count = false")
    item("Confirmar que o contador NÃO aparece")
    espaco()

    subtitulo("8. Quantidade restante (show_remaining)")
    item("Abrir cupom com show_remaining = true e total_quantity > 0")
    item("Confirmar que aparece \"X restantes\" (total - resgates)")
    item("Resgatar uma vez e confirmar que o número diminuiu")
    espaco()

    subtitulo("9. Cupons em destaque (featured)")
    item("Verificar que cupons com featured = true aparecem no topo")
    item("Confirmar que têm badge ou marcação visual de destaque")
    item("Cupons sem destaque devem vir depois, por mais recente")
    espaco()

    subtitulo("10. Cupom com início futuro (start_date)")
    item("Mudar start_date de um cupom para amanhã")
    item("Confirmar que ele NÃO aparece na listagem do consumidor")
    item("Mudar start_date para hoje — deve aparecer normalmente")
    espaco()

    subtitulo("11. Link do WhatsApp das empresas")
    item("Abrir a página de uma empresa")
    item("Clicar no botão/link de WhatsApp")
    item("Confirmar que abre o wa.me com o número correto")
    item("Testar em celular — deve abrir direto no WhatsApp")
    espaco()

    subtitulo("12. Seção de regras do cupom")
    item("Abrir um cupom que tem o campo rules preenchido")
    item("Confirmar que a seção \"Regras de uso\" aparece")
    item("Abrir um cupom com rules vazio")
    item("Confirmar que a seção NÃO aparece (sem espaço em branco)")

    rodape()

    c.save()
    print(f"PDF gerado: {path}")

gerar_pdf()
