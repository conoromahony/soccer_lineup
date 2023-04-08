# users/views.py

from django.shortcuts import render

def users_dashboard(request):
    return render(request, "users/dashboard.html",)