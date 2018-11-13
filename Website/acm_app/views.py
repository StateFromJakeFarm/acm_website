from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required

from . import forms
from .file_funcs import store_uploaded_file

def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "register.html")

def home(request):
    return render(request, "home.html")

def problems(request):
    if request.method == 'POST':
        # Handle problem submission uploads
        form = forms.ProblemSubmissionForm(request.POST, request.FILES)
        # Save file locally (on shared volume?) so Grader and CodeRunner can
        # use it
        store_uploaded_file(request.FILES['submission'], '/tmp')

    return render(request, "problem.html")

def leaderboard(request):
    return render(request, "home.html")
