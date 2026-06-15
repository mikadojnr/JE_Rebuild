# tasks.py
from extensions import mail
from flask_mail import Message
from celery_config import celery   # ← Import the celery instance here

@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, subject, recipient, html):
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=html,
            sender=app.config.get('MAIL_DEFAULT_SENDER')  # Will work inside context
        )
        mail.send(msg)
        print(f"✅ Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Failed sending to {recipient}: {e}")
        raise self.retry(exc=e)