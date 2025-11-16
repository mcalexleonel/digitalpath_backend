from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_contact_email_task(self, contact_message_id):
    """
    Send contact form email and update database record.

    Args:
        contact_message_id: ID of the ContactMessage model instance
    """
    from .models import ContactMessage

    try:
        contact_message = ContactMessage.objects.get(id=contact_message_id)

        # Build email content
        subject = f"New Contact Form Submission from {contact_message.name}"
        message = (
            f"From: {contact_message.name} <{contact_message.email}>\n"
            f"Contact Form Submission\n"
            f"***********************\n\n"
            f"{contact_message.message}\n\n"
            f"---\n"
            f"Submitted at: {contact_message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )

        # Send email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],
            fail_silently=False
        )

        # Update status to sent
        contact_message.status = 'sent'
        contact_message.sent_at = timezone.now()
        contact_message.error_message = None
        contact_message.save()

        logger.info(f"Contact email sent successfully for message ID {contact_message_id}")

    except ContactMessage.DoesNotExist:
        logger.error(f"ContactMessage with ID {contact_message_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error sending contact email: {e}", exc_info=True)

        # Update status to failed
        try:
            contact_message = ContactMessage.objects.get(id=contact_message_id)
            contact_message.status = 'failed'
            contact_message.error_message = str(e)
            contact_message.save()
        except Exception as update_error:
            logger.error(f"Error updating contact message status: {update_error}")

        # Retry the task
        raise self.retry(exc=e, countdown=60)
