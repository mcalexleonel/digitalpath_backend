from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages

from .tasks import send_email_task
import logging
logger = logging.getLogger(__name__)


def contact_view(request):
    return render(request, "contact/main.html", {})

def mail_contact(request):
    if request.method == "POST":
        name = 'demo'
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")


        full_message = (
            f"From: {name} <{email}>\n"
            f"Contact Form Submission\n"
            f"***********************\n"
            f"{message}"
        )

        try:
            send_email_task(subject, full_message, [settings.EMAIL_HOST_USER])                   
            messages.success(request, "✅ Your message has been sent successfully!")
        except Exception as e:
            logger.error(f"Error sending contact email: {e}", exc_info=True)
            messages.error(request, "❌ Error sending message. Please try again later.")

        # Si es una solicitud HTMX, devolvemos solo el bloque de mensajes
        if request.headers.get("HX-Request"):
            return render(request, "partials/contact_messages.html", {"messages": messages.get_messages(request)})

    # Si no es HTMX, se comporta normal
    return redirect("contact")


   