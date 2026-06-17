# utils.py
from flask_mail import Message
from extensions import mail
from flask import current_app

def send_newsletter_email(subject: str, html_content: str, recipient: str):
    """Send newsletter email with proper error handling"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=html_content,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)
        print(f"✅ Newsletter sent to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Failed to send newsletter to {recipient}: {e}")
        return False