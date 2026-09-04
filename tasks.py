# tasks.py
import logging
from extensions import mail
from flask_mail import Message
from celery_config import celery

logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, subject, recipient, html_content):
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=html_content
        )
        mail.send(msg)
        logger.info("Email sent to %s", recipient)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", recipient, e)
        raise self.retry(exc=e)