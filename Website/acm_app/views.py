from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required

from . import forms
from . import models
from .helpers import store_uploaded_file, run_submission

def login(request):
    '''
    Send user to login page
    '''
    return render(request, 'registration/login.html')

def logout_view(request):
    '''
    Log user out and redirect to homepage
    '''
    logout(request)

    return redirect('/')

def register(request):
    '''
    Create and process account creation form
    '''
    if request.method == 'POST':
        # Use form response to create new account
        registration_form = forms.RegistrationForm(request.POST)
        if registration_form.is_valid():
            registration_form.save(commit=True)
            return redirect('/')
    else:
        # Present form to user
        registration_form = forms.RegistrationForm()
    
    context = {
        'form': registration_form
    }

    return render(request, 'registration/register.html', context=context)

def home(request):
    '''
    Render homepage.
    '''
    return render(request, 'home.html')

def problems(request):

    code = ''

    if request.method == 'POST':
        # Handle problem submission uploads
        submission_form = forms.ProblemSubmissionForm(request.POST, request.FILES)

        # Save file locally (on shared volume?) so Grader and CodeRunner can
        # use it
        local_file_path = store_uploaded_file(request.FILES['solution_file'], '/tmp')

        # Tell grader/backend container to run this code
        code = run_submission(local_file_path).decode('utf-8')

    else:
        # Present form to user
        submission_form = forms.ProblemSubmissionForm()

    context = {
        'form': submission_form,
        'code' : code
    }

    return render(request, 'problem.html', context=context)

def leaderboard(request):
    '''
    TODO: Render leaderboard
    '''
    return render(request, 'home.html')

@login_required
def create_or_edit_problem(request):
    '''
    Handle problem creation and editing
    '''
    if request.method == 'POST':
        # Use submitted form to create/update problem info within model
        edit_form = forms.CreateOrEditProblemForm(request.POST)
        if edit_form.is_valid():
            edited = models.ProblemModel(
                title = edit_form.cleaned_data['title'],
                slug = slugify(edit_form.cleaned_data['title']),
                description = edit_form.cleaned_data['description'],
                author = request.user
            )
            edited.save()
    else:
        # Present form to user
        edit_form = forms.CreateOrEditProblemForm()

    context = {
        'form': edit_form
    }

    return render(request, 'edit.html', context=context)
