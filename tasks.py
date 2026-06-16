# tasks.py
from extensions import mail
from flask_mail import Message
from celery_config import celery

@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, subject, recipient, html_content):
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=html_content
        )
        mail.send(msg)
        print(f"✅ Sent to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Failed {recipient}: {e}")
        raise self.retry(exc=e)