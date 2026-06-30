# utils.py
from flask_mail import Message
from extensions import mail
from flask import current_app, render_template, url_for

def send_newsletter_email(subject: str, html_content: str, recipient: str, newsletter_url=None):
    """Send newsletter email"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )

        msg.html = render_template('emails/newsletter.html',
                                   subject=subject,
                                   content=html_content,
                                   newsletter_url=newsletter_url,
                                   recipient_email=recipient)

        mail.send(msg)
        print(f"Newsletter sent to {recipient}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send newsletter to {recipient}: {e}")
        print(f"Failed to send newsletter to {recipient}: {e}")
        return False


def send_activation_email(user, token):
    """Send account activation email"""
    try:
        activation_url = url_for('public.activate_account', token=token, _external=True)

        msg = Message(
            subject="Activate Your Admin Account - John & Eniola Consultancy",
            recipients=[user.email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )

        msg.html = render_template(
            'emails/activation.html',
            user=user,
            activation_url=activation_url
        )

        mail.send(msg)
        print(f"Activation email sent to {user.email}")
        return True

    except Exception as e:
        current_app.logger.error(f"Activation email failed for {user.email}: {e}")
        print(f"Activation email failed: {e}")
        return False


def send_password_reset_email(user, token):
    """Send password reset email"""
    try:
        reset_url = url_for('public.reset_password', token=token, _external=True)

        msg = Message(
            subject="Reset Your Password - John & Eniola Consultancy",
            recipients=[user.email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )

        msg.html = render_template(
            'emails/password_reset.html',
            user=user,
            reset_url=reset_url
        )

        mail.send(msg)
        print(f"Password reset email sent to {user.email}")
        return True

    except Exception as e:
        current_app.logger.error(f"Password reset email failed for {user.email}: {e}")
        print(f"Password reset email failed: {e}")
        return False


def send_testimonial_invite_email(submission, submission_url, days_remaining=7):
    """Send testimonial submission invitation"""
    try:
        msg = Message(
            subject="Share Your Experience with John & Eniola Consultancy",
            recipients=[submission.email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        msg.html = render_template(
            'emails/testimonial_invite.html',
            submission=submission,
            submission_url=submission_url,
            days_remaining=days_remaining
        )
        
        mail.send(msg)
        print(f"Testimonial invite sent to {submission.email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send testimonial invite to {submission.email}: {e}")
        print(f"Failed to send testimonial invite: {e}")
        return False