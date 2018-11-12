from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.


def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "register.html")

@login_required
def home(request):
    return render(request, "home.html")
