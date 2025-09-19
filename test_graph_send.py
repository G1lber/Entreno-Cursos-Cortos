import requests
import webbrowser
import json
import os

# 🔑 Datos de tu app
tenant_id = "consumers"  # para Hotmail/Outlook personal
client_id = "bd7ebf26-a29c-4197-97b4-fba9ff43cd9e"
client_secret = "kIi8Q~IUuBGkkO7JR9aczVkUvt3rQfXroO5bOddF"
redirect_uri = "https://jwt.ms"

# 📧 Correos
to_email = "daniels_caicedo@soy.sena.edu.co"

# 📂 Guardamos tokens en un archivo
TOKENS_FILE = "tokens.json"

def get_tokens_with_auth_code():
    """Primera vez: abre navegador, obtiene auth_code y cambia por access+refresh tokens"""
    auth_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&response_mode=query"
        f"&scope=openid profile offline_access https://graph.microsoft.com/Mail.Send"
        f"&state=12345"
    )
    print("👉 Abre esta URL en tu navegador y copia el 'code':\n", auth_url)
    webbrowser.open(auth_url)

    auth_code = input("Pega aquí el 'code' de la URL: ")

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/Mail.Send offline_access openid profile",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "client_secret": client_secret,
    }
    token_response = requests.post(token_url, data=token_data)
    tokens = token_response.json()
    print("TOKEN RESPONSE:", tokens)

    # Guardar en archivo
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f)

    return tokens


def refresh_tokens(refresh_token):
    """Usar el refresh token para obtener un nuevo access_token"""
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/Mail.Send offline_access openid profile",
        "refresh_token": refresh_token,
        "redirect_uri": redirect_uri,
        "grant_type": "refresh_token",
        "client_secret": client_secret,
    }
    token_response = requests.post(token_url, data=token_data)
    tokens = token_response.json()
    print("REFRESH RESPONSE:", tokens)

    if "access_token" in tokens:
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f)
    return tokens


def get_access_token():
    """Devuelve un access_token válido usando archivo de tokens"""
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)

        refresh_token_val = tokens.get("refresh_token")
        return refresh_tokens(refresh_token_val)
    else:
        return get_tokens_with_auth_code()


# 1️⃣ Obtener access_token (desde archivo o refresh)
tokens = get_access_token()
access_token = tokens.get("access_token")

# 2️⃣ Enviar correo
send_url = "https://graph.microsoft.com/v1.0/me/sendMail"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}
email_msg = {
    "message": {
        "subject": "Prueba con Refresh Token 🚀",
        "body": {"contentType": "Text", "content": "Hola! Este correo salió sin volver a loguearme."},
        "toRecipients": [{"emailAddress": {"address": to_email}}],
    }
}
send_response = requests.post(send_url, headers=headers, json=email_msg)
print("SEND RESPONSE:", send_response.status_code, send_response.text)
