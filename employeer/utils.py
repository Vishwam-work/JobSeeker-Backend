import random
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_otp():
    return str(random.randint(100000, 999999))

def send_email(to_email, subject,template_name,context):
    env = Environment(
        loader=FileSystemLoader(os.path.join(BASE_DIR, "templates"))
    )
    template = env.get_template(template_name)
    html_content = template.render(context)
    message = Mail(
        from_email="ruchi@nvglobaltech.com",
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(os.environ.get("SECRET_KEY"))
        sg.send(message)
        return True
    except Exception as e:
        print("SendGrid Error:", e)
        return False
