"""
Script de verificação de conexão com Google Ads.
Execute antes de iniciar o servidor MCP para confirmar que tudo está configurado.

Uso:
    python test_connection.py
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()


def check_env():
    required = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print("❌  Variáveis faltando no .env:")
        for k in missing:
            print(f"    - {k}")
        return False
    print("✅  Todas as variáveis de ambiente encontradas")
    return True


def check_import():
    try:
        from google.ads.googleads.client import GoogleAdsClient
        print("✅  google-ads instalado corretamente")
        return True
    except ImportError as e:
        print(f"❌  Erro ao importar google-ads: {e}")
        print("    Execute: pip install -r requirements.txt")
        return False


def check_connection():
    try:
        from mcp_server.auth import get_client, get_login_customer_id
        client = get_client()
        mcc_id = get_login_customer_id()

        service = client.get_service("GoogleAdsService")
        query = """
            SELECT customer.id, customer.descriptive_name, customer.currency_code
            FROM customer
            LIMIT 1
        """
        response = service.search(customer_id=mcc_id, query=query)
        for row in response:
            c = row.customer
            print(f"✅  Conectado! Conta: {c.descriptive_name} (ID: {c.id}) | Moeda: {c.currency_code}")
        return True
    except Exception as e:
        print(f"❌  Falha na conexão: {e}")
        return False


def check_mcc_accounts():
    try:
        from mcp_server.auth import get_client, get_login_customer_id
        from mcp_server.tools.accounts import list_accounts
        client = get_client()
        mcc_id = get_login_customer_id()
        accs = list_accounts(client, mcc_id)
        print(f"✅  MCC tem {len(accs)} conta(s) gerenciada(s):")
        for a in accs[:5]:
            print(f"    • {a['name']} (ID: {a['id']}) — {a['status']}")
        if len(accs) > 5:
            print(f"    ... e mais {len(accs) - 5} conta(s)")
        return True
    except Exception as e:
        print(f"❌  Erro ao listar contas MCC: {e}")
        return False


def main():
    print()
    print("=" * 55)
    print("  Verificação de Conexão — Google Ads MCC")
    print("=" * 55)
    print()

    steps = [
        ("Verificando variáveis de ambiente", check_env),
        ("Verificando biblioteca google-ads", check_import),
        ("Testando autenticação com a API", check_connection),
        ("Listando contas da MCC", check_mcc_accounts),
    ]

    passed = 0
    for label, fn in steps:
        print(f"→ {label}...")
        ok = fn()
        if ok:
            passed += 1
        else:
            print()
            print(f"⚠️  Corrija o erro acima antes de continuar.")
            break
        print()

    print("=" * 55)
    if passed == len(steps):
        print("🎉  Tudo pronto! O servidor MCP está configurado.")
        print()
        print("   Para iniciar o servidor manualmente:")
        print("   python -m mcp_server.server")
        print()
        print("   O Claude Code carrega automaticamente via .claude/settings.json")
    else:
        print(f"   {passed}/{len(steps)} verificações passaram.")
        print("   Siga o guia em CLAUDE.md para concluir a configuração.")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
