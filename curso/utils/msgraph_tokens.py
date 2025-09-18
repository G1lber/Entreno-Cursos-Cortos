# utils/msgraph_tokens.py
import os
import json
import requests
from django.conf import settings

TOKENS_FILE = os.path.join(settings.BASE_DIR, "tokens.json")

def get_tokens_from_file():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    return None

def save_tokens(tokens):
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f)

def refresh_access_token():
    tokens = get_tokens_from_file()
    if not tokens or "refresh_token" not in tokens:
        raise Exception("❌ No hay refresh_token guardado. Primero inicia sesión y guárdalo en tokens.json")

    refresh_token = tokens["refresh_token"]
    token_url = f"https://login.microsoftonline.com/{settings.MSGRAPH_TENANT_ID}/oauth2/v2.0/token"
    token_data = {
        "client_id": settings.MSGRAPH_CLIENT_ID,
        "scope": "https://graph.microsoft.com/Mail.Send offline_access openid profile",
        "refresh_token": refresh_token,
        "redirect_uri": settings.MSGRAPH_REDIRECT_URI,  # 👈 configurable
        "grant_type": "refresh_token",
        "client_secret": settings.MSGRAPH_CLIENT_SECRET,
    }

    r = requests.post(token_url, data=token_data)
    new_tokens = r.json()

    if "access_token" in new_tokens:
        save_tokens(new_tokens)
        return new_tokens["access_token"]

    raise Exception(f"❌ Error refrescando token: {new_tokens}")

def get_access_token():
    """
    Devuelve un access_token válido.
    Si no existe o expiró, lo renueva automáticamente.
    """
    tokens = get_tokens_from_file()
    if not tokens:
        raise Exception("⚠️ No hay tokens.json. Haz primero el login inicial con authorization_code.")

    # Siempre intentamos refrescar para garantizar validez
    return refresh_access_token()
