from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.


def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "register.html")

def home(request):
    return render(request, "home.html")

def problems(request):
    return render(request, "home.html")

def leaderboard(request):
    return render(request, "home.html")
