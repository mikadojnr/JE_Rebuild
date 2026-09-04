# utils.py
import re
from flask_mail import Message
from extensions import mail
from flask import current_app, render_template, url_for


def is_suspicious_email(email):
    """Heuristic check for bot-generated email addresses."""
    if not email:
        return False

    local_part = email.split('@')[0].lower()

    # Strip common separators for pill test
    compact = re.sub(r'[\.\-_]', '', local_part)

    # 1. Only letters/digits after removing separators (no separators at all)
    #    -> looks like a random keyboard mash
    if re.fullmatch(r'[a-z0-9]+', compact):
        # 2. Dots between most characters, e.g. s.a.s.i.zoyof.o7.19
        if local_part.count('.') >= 4:
            return True
        # 3. Very long random alphanumeric run
        if len(compact) >= 20 and not re.search(r'[aeiou]{3}', compact):
            return True
        # 4. Alternating pattern like c.o.n.s.o.n.a.n.t.v.o.w.e.l
        if re.fullmatch(r'(?:[bcdfghjklmnpqrstvwxyz][aeiou]){4,}', compact):
            return True
        # 5. Repeated segments like aba.ba.b.a or a.b.a.b.a
        if local_part.count('.') >= 3 and len(set(compact)) <= 5:
            return True

    # 6. Known bulk/Gmail formatting weirdness: more than 6 parts
    if local_part.count('.') >= 6:
        return True

    # 7. Dotted name + trailing 2+ digit number, e.g. p.c.haziti93, ade.a.nm27
    if local_part.count('.') >= 2 and re.search(r'(?<!\d)\d{2,}$', local_part):
        return True

    return False


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
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send newsletter to {recipient}: {e}")
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
        return True

    except Exception as e:
        current_app.logger.error(f"Activation email failed for {user.email}: {e}")
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
        return True

    except Exception as e:
        current_app.logger.error(f"Password reset email failed for {user.email}: {e}")
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
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send testimonial invite to {submission.email}: {e}")
        return False