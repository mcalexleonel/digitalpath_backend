from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def services_view(request):
    return render(request, "services/main.html", {})