import os

import requests
import systems.utils

API_KEY = os.getenv("BREVO_API_KEY")


def send_reset_email(to, pwd):
    print(to)
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "api-key": API_KEY,
            "content-type": "application/json",
        },
        json={
            "sender": {"name": "Jorm", "email": "noreply@jorm.kurowski.xyz"},
            "to": [{"email": to}],
            "subject": "Jorm Temporary Password",
            "textContent": f"""Hello, your temporary password is:
                {pwd}

                You will need to change your password after you log in
                "setting password [new password]"

                This ONE TIME password will not work next time you try to log in.""",
        },
    )
    systems.utils.debug_print(response.status_code, response.json())
