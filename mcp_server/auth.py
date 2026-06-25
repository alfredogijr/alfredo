"""Google Ads API authentication."""
import os
from pathlib import Path
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv()


def get_client(customer_id: str | None = None) -> GoogleAdsClient:
    """Create authenticated Google Ads client."""
    config = {
        "developer_token": _require("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": _require("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": _require("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": _require("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": _require("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    }
    client = GoogleAdsClient.load_from_dict(config)
    return client


def get_login_customer_id() -> str:
    return _require("GOOGLE_ADS_LOGIN_CUSTOMER_ID")


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(
            f"Variável de ambiente obrigatória não definida: {key}\n"
            f"Copie .env.example para .env e preencha os valores."
        )
    return val
