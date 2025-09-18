import requests
import webbrowser
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand


TOKENS_FILE = os.path.join(settings.BASE_DIR, "tokens.json")


class Command(BaseCommand):
    help = "Inicializa Microsoft Graph con login y guarda tokens.json"

    def handle(self, *args, **options):
        tenant_id = settings.MSGRAPH_TENANT_ID
        client_id = settings.MSGRAPH_CLIENT_ID
        client_secret = settings.MSGRAPH_CLIENT_SECRET
        redirect_uri = settings.MSGRAPH_REDIRECT_URI

        # 1️⃣ Abrir navegador para login
        auth_url = (
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
            f"?client_id={client_id}"
            f"&response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&response_mode=query"
            f"&scope=openid profile offline_access https://graph.microsoft.com/Mail.Send"
            f"&state=12345"
        )
        self.stdout.write(self.style.SUCCESS("👉 Abre este link y loguéate:"))
        self.stdout.write(auth_url)
        webbrowser.open(auth_url)

        # 2️⃣ Pide el code al usuario
        auth_code = input("\nPega aquí el 'code' que salió en la URL: ").strip()

        # 3️⃣ Intercambia el code por tokens
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            "client_id": client_id,
            "scope": "https://graph.microsoft.com/Mail.Send offline_access openid profile",
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "client_secret": client_secret,
        }
        r = requests.post(token_url, data=token_data)
        tokens = r.json()

        if "access_token" in tokens:
            with open(TOKENS_FILE, "w") as f:
                json.dump(tokens, f, indent=2)

            self.stdout.write(self.style.SUCCESS(f"✅ Tokens guardados en {TOKENS_FILE}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Error obteniendo tokens: {tokens}"))
