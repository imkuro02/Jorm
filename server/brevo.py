import requests
import os
import utils

API_KEY = os.getenv("BREVO_API_KEY")

def send_reset_email(to, pwd):
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "api-key": API_KEY,
            "content-type": "application/json",
        },
        json={
            "sender": {"name": "Your App", "email": "reset_account@jorm.kurowski.xyz"},
            "to": [{"email": to}],
            "subject": "Jorm Temporary Password",
            "textContent": f"Hello, your temporary password is:\n\n\n{pwd}\n\n\nPlease change it after you log in!!!"
        }
    )
    utils.debug_print(response.status_code, response.json())
