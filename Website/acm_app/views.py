import os

from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout, login, authenticate
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.core.files.storage import DefaultStorage
from django.conf import settings

from . import forms
from . import models
from .helpers import store_uploaded_file, run_submission


# def login_view(request):
#     '''
#     Send user to login page
#     '''
#     return render(request, 'registration/login.html')


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
            new_user = authenticate(username=registration_form.cleaned_data['username'],
                                    password=registration_form.cleaned_data['password1'],
                                    )
            login(request, new_user)
            return redirect('/')
    else:
        # Present form to user
        registration_form = forms.RegistrationForm()

    context = {
        'form': registration_form,
        'nbar' : "Register"
    }

    return render(request, 'registration/register.html', context=context)


def home(request):
    '''
    Render homepage.
    '''
    context = {
        'nbar' : 'Home'
    }

    return render(request, 'home.html', context=context)


def all_problems(request):

    context = {
        'problems': models.ProblemModel.objects.all().order_by('-id'),
        'nbar' : 'Problems'
    }

    return render(request, 'all_problems.html', context=context)


def problem(request, slug=''):

    test_results = ''

    if request.method == 'POST':
        submission_form = forms.ProblemSubmissionForm(
            request.POST, request.FILES)
        if submission_form.is_valid():
            local_file_path = store_uploaded_file(
                request.FILES['solution_file'], '/tmp')
            problem = models.ProblemModel.objects.get(slug=slug)
            testcases_path = os.path.join(
                settings.MEDIA_ROOT, str(problem.testcases))
            test_results = run_submission(
                local_file_path, testcases_path).decode('utf-8').strip()
    else:
        # Present form to user
        submission_form = forms.ProblemSubmissionForm()

    context = {
        'test_results': test_results,
        'form': submission_form,
        'nbar': 'Problems'
    }

    return render(request, 'problem.html', context=context)


def leaderboard(request):
    '''
    TODO: Render leaderboard
    '''
    context = {
        'nbar': 'Leaderboard'
    }

    return render(request, 'home.html', context=context)


@login_required
def create_or_edit_problem(request):
    '''
    Handle problem creation and editing
    '''
    if request.method == 'POST':
        # Use submitted form to create/update problem info within model
        edit_form = forms.CreateOrEditProblemForm(request.POST, request.FILES)
        if edit_form.is_valid():
            edited = models.ProblemModel(
                title=edit_form.cleaned_data['title'],
                slug=slugify(edit_form.cleaned_data['title']),
                description=edit_form.cleaned_data['description'],
                author=request.user,
                testcases=request.FILES['testcases']
            )
            edited.save()
            return redirect('/problems')
    else:
        # Present form to user
        edit_form = forms.CreateOrEditProblemForm()

    context = {
        'form': edit_form,
        'nbar': 'Problems'
    }

    return render(request, 'edit.html', context=context)
