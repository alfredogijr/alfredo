"""
Script para configurar autenticação OAuth2 com o Google Ads.
Execute este script UMA VEZ para obter o refresh_token.

Uso:
    python setup_auth.py

Pré-requisitos:
    1. Crie um projeto no Google Cloud Console
    2. Ative a Google Ads API
    3. Crie credenciais OAuth2 (tipo: Desktop app)
    4. Baixe o JSON de credenciais
"""
import os
import json
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]

OAUTH_REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"


def run_setup():
    print("=" * 60)
    print("  Configuração OAuth2 - Google Ads MCC")
    print("=" * 60)
    print()

    # Verifica se o arquivo de credenciais existe
    client_secrets = input(
        "Caminho para o arquivo client_secret.json (ou pressione Enter para digitar manualmente): "
    ).strip()

    if client_secrets and Path(client_secrets).exists():
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets, scopes=SCOPES)
    else:
        print("\nDigite as credenciais manualmente:")
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()

        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [OAUTH_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

    flow.redirect_uri = OAUTH_REDIRECT_URI

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    print("\n1. Abra este URL no seu navegador:")
    print(f"\n   {auth_url}\n")
    print("2. Faça login com a conta Google Ads")
    print("3. Autorize o acesso")
    print("4. Copie o código de autorização\n")

    auth_code = input("Cole o código de autorização aqui: ").strip()

    flow.fetch_token(code=auth_code)
    credentials = flow.credentials

    print("\n✅ Autenticação bem-sucedida!\n")
    print("Adicione estas variáveis ao seu arquivo .env:\n")
    print(f"GOOGLE_ADS_CLIENT_ID={credentials.client_id}")
    print(f"GOOGLE_ADS_CLIENT_SECRET={credentials.client_secret}")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}")

    # Salva automaticamente no .env se existir
    env_path = Path(".env")
    if env_path.exists():
        save = input("\nDeseja salvar automaticamente no .env? (s/n): ").strip().lower()
        if save == "s":
            lines = env_path.read_text().splitlines()
            new_lines = []
            keys_updated = set()

            for line in lines:
                if line.startswith("GOOGLE_ADS_CLIENT_ID="):
                    new_lines.append(f"GOOGLE_ADS_CLIENT_ID={credentials.client_id}")
                    keys_updated.add("client_id")
                elif line.startswith("GOOGLE_ADS_CLIENT_SECRET="):
                    new_lines.append(f"GOOGLE_ADS_CLIENT_SECRET={credentials.client_secret}")
                    keys_updated.add("client_secret")
                elif line.startswith("GOOGLE_ADS_REFRESH_TOKEN="):
                    new_lines.append(f"GOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}")
                    keys_updated.add("refresh_token")
                else:
                    new_lines.append(line)

            if "refresh_token" not in keys_updated:
                new_lines.append(f"GOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}")

            env_path.write_text("\n".join(new_lines) + "\n")
            print("✅ Arquivo .env atualizado!")


if __name__ == "__main__":
    run_setup()
