from flask_mail import Message
from extensions import mail

def send_newsletter_email(subject, html_content, recipient_email):
    """Helper function to send single email"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=html_content
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error to {recipient_email}: {e}")
        return False