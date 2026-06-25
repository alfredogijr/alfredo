"""
Gera o Refresh Token para autenticacao com o Google Ads.
Execute este script para (re)autenticar.
"""
import os
import webbrowser
import urllib.parse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def main():
    print()
    print("=" * 55)
    print("  Autenticacao Google Ads — Gerando Refresh Token")
    print("=" * 55)
    print()

    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        print("Nao encontrei Client ID ou Client Secret no .env")
        print("Cole abaixo:")
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()

    # Gerar URL de autorizacao (sem PKCE para simplificar)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "scope": "https://www.googleapis.com/auth/adwords",
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)

    print("Abrindo o navegador para autorizar...")
    print()
    webbrowser.open(auth_url)

    print("Se o navegador nao abrir, copie e acesse este link:")
    print()
    print(auth_url)
    print()
    print("-" * 55)
    print("1. Faca login com a conta Google Ads")
    print('2. Clique em "Permitir"')
    print("3. Copie o codigo que aparecer na tela")
    print("-" * 55)
    print()

    auth_code = input("Cole o codigo aqui: ").strip()

    # Trocar codigo por refresh token
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "grant_type": "authorization_code",
    })

    data = resp.json()
    if "refresh_token" not in data:
        print(f"\n[ERRO] {data.get('error_description', data)}")
        input("\nPressione Enter para fechar...")
        return

    refresh_token = data["refresh_token"]
    print(f"\n[OK] Refresh Token gerado!")

    # Salvar no .env
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        if "GOOGLE_ADS_REFRESH_TOKEN=" in content:
            lines = []
            for line in content.splitlines():
                if line.startswith("GOOGLE_ADS_REFRESH_TOKEN="):
                    lines.append(f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")
                else:
                    lines.append(line)
            env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            with env_path.open("a", encoding="utf-8") as f:
                f.write(f"\nGOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n")
        print("[OK] Salvo no .env automaticamente!")
    else:
        print(f"\nAdicione ao seu .env:")
        print(f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")

    print()
    print("=" * 55)
    print("  Autenticacao concluida!")
    print("  Agora rode: python test_connection.py")
    print("=" * 55)
    print()
    input("Pressione Enter para fechar...")


if __name__ == "__main__":
    main()
