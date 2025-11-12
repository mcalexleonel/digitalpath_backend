from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def portfolio_view(request):
    return render(request, "portfolio/main.html", {})