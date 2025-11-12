from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, message, recipient_list):
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Error sending email: {e}", exc_info=True)
        # raise self.retry(exc=e, countdown=60, max_retries=3)  # reintenta si quieres
        raise self.retry(exc=e, countdown=60)
