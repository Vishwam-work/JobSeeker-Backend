import os
import secrets
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def send_email(to_email, subject, template_name, context):
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
        sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
        sg.send(message)
        return True
    except Exception:
        logger.exception("SendGrid email failed")
        return False
