from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required

from . import forms
from .helpers import store_uploaded_file, run_submission

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
        local_file_path = store_uploaded_file(request.FILES['submission'], '/tmp')

        # Tell grader/backend container to run this code
        print(run_submission(local_file_path))

    return render(request, "problem.html")

def leaderboard(request):
    return render(request, "home.html")
