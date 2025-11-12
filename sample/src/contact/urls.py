
from django.urls import path

from . import views

urlpatterns = [
    path("", views.contact_view, name='contact'),
    path("mail_contact/", views.mail_contact, name='mail_contact'),
]
