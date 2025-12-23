import random
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email(to_email, subject, content):
    message = Mail(
        from_email="ruchi@nvglobaltech.com",
        to_emails=to_email,
        subject=subject,
        plain_text_content=content,
    )

    try:
        sg = SendGridAPIClient(os.environ.get("SECRET_KEY"))
        sg.send(message)
        return True
    except Exception as e:
        print("SendGrid Error:", e)
        return False