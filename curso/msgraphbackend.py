import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from curso.utils.msgraph_tokens import refresh_access_token

class MSGraphBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0
        for message in email_messages:
            try:
                access_token = refresh_access_token()

                send_url = "https://graph.microsoft.com/v1.0/me/sendMail"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }
                email_msg = {
                    "message": {
                        "subject": message.subject,
                        "body": {
                            "contentType": "HTML",   # 👈 importante
                            "content": message.body, # aquí ya pasará el HTML
                        },
                        "toRecipients": [{"emailAddress": {"address": addr}} for addr in message.to],
                    }
                }


                r = requests.post(send_url, headers=headers, json=email_msg)
                print("📨 SEND RESPONSE:", r.status_code, r.text)  # 👈 debug

                if r.status_code == 202:
                    sent_count += 1
                else:
                    print("❌ Error enviando:", r.json())

            except Exception as e:
                print("⚠️ Excepción en send_messages:", str(e))

        return sent_count
