import os
import secrets
import logging
from sendgrid.helpers.mail import Mail
from jinja2 import Environment, FileSystemLoader
from django.contrib.auth.tokens import PasswordResetTokenGenerator,default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def send_email(to_email, subject, template_name, context):
    try:
        html_content = render_to_string(
            template_name,
            context
        )

        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.SYSTEM_EMAIL_FROM_EMAIL,
            to=[to_email],
        )

        email.content_subtype = "html"

        email.send(fail_silently=False)

        return True

    except Exception:
        logger.exception("SMTP email failed")
        return False


class CustomTokenGenerator(PasswordResetTokenGenerator):
    pass

password_reset_token = CustomTokenGenerator()
