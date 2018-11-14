from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from . import forms
from .helpers import store_uploaded_file, run_submission

def login(request):
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def register(request):
    if request.method == 'POST':
        registration_form = forms.RegistrationForm(request.POST)
        print(request.GET)
        if registration_form.is_valid():
            registration_form.save(commit=True)
            return redirect('/')
    else:
        registration_form = forms.RegistrationForm()
    
    context = {
        'form': registration_form
    }
    return render(request, 'registration/register.html', context=context)

def home(request):
    return render(request, 'home.html')

def problems(request):
    if request.method == 'POST':
        # Handle problem submission uploads
        form = forms.ProblemSubmissionForm(request.POST, request.FILES)

        # Save file locally (on shared volume?) so Grader and CodeRunner can
        # use it
        local_file_path = store_uploaded_file(request.FILES['solution_file'], '/tmp')

        # Tell grader/backend container to run this code
        print(run_submission(local_file_path))
    else:
        form = forms.ProblemSubmissionForm()

    context = {
        'form': form
    }

    return render(request, 'problem.html', context=context)

def leaderboard(request):
    return render(request, 'home.html')
