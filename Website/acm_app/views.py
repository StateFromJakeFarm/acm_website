import os
import tarfile

from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout, login, authenticate
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.core.files.storage import DefaultStorage
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import permission_required
from django.db.models import F

import json



from . import forms
from . import models
from . import helpers
from markdown import markdown


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

            # Create leaderboard entry for this user
            models.LeaderboardModel(user=new_user).save()

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


def display_problems(request, contest_slug=None):
    '''
    Display all problems
    '''
    contest = None
    if contest_slug:
        # Grab all problems from requested contest
        contest = helpers.get_contest_record(contest_slug)
        problems = models.ProblemModel.objects.filter(contest=contest).order_by('-id')
    else:
        # Grab all problems not belonging to any contest
        problems = models.ProblemModel.objects.filter(contest=None).order_by('-id')

    context = {
        'problems': problems,
        'nbar' : 'Contests' if contest else 'Problems',
    }

    if contest:
        # Display contest name
        context['contest_name'] = contest.name

    return render(request, 'display_problems.html', context=context)


def problem(request, slug=''):

    # Get problem object from database
    problem = helpers.get_problem_record(slug)
    if not problem:
        raise Exception('"{}" does not identify a problem'.format(slug))

    text_results = ''

    if request.method == 'POST':
        # Handle problem submission
        submission_form = forms.ProblemSubmissionForm(
            request.POST, request.FILES)
        if submission_form.is_valid():
            # Save file to /tmp
            local_file_path = helpers.store_uploaded_file(
                request.FILES['solution_file'], '/tmp')

            # Grab testcases for this problem
            testcases_path = os.path.join(
                settings.MEDIA_ROOT, str(problem.testcases))

            # Run submission and get results from grader container
            test_results = helpers.run_submission(local_file_path, testcases_path, problem.time_limit)

            text_results = test_results['text']
            boolean_result = test_results['result']

            if boolean_result and \
                not helpers.user_has_solved_problem(request.user, problem):
                # update leaderboard if solved
                # verify correctness and award a point if winner
                leaderboard_entry = models.LeaderboardModel.objects.get(user=request.user)
                leaderboard_entry.score = F('score') + 1 # F is atomic or something and avoids race condition
                leaderboard_entry.save()

                # Record that user has solved this problem
                solved_problem_entry = models.UserSolvedProblems(user=request.user, problem=problem)
                solved_problem_entry.save()

        return HttpResponse(text_results)

    else:
        # Present form to user
        submission_form = forms.ProblemSubmissionForm()

        context = {
            'slug' : slug,
            'description': markdown(problem.description),
            'test_results': text_results,
            'form': submission_form,
            'time_limit': problem.time_limit,
            'memswap_limit': problem.memswap_limit,
            'nbar': 'Problems'
        }
        if problem.contest:
            context['contest'] = problem.contest.name

        return render(request, 'problem.html', context=context)


def leaderboard(request):
    '''
    Render leaderboard
    '''

    leaderboard = models.LeaderboardModel.objects.all().order_by('score').reverse()

    context = {
        'nbar': 'Leaderboard',
        'leaderboard' : leaderboard
    }

    return render(request, 'leaderboard.html', context=context)

@login_required
@permission_required('user.is_staff', raise_exception=True)
def create_or_edit_problem(request, slug=''):
    '''
    Handle problem creation and editing
    '''

    # Get info about this problem if it already exists
    problem = None
    problem_info = {}
    if slug != '':
        # Grab info for an existing problem
        problem = helpers.get_problem_record(slug)
        if problem:
            problem_info = {
                'title': problem.title,
                'description': problem.description,
                'time_limit': problem.time_limit,
                'mem_limit': problem.mem_limit,
                'memswap_limit': problem.memswap_limit,
                'contest': problem.contest.name
            }
        else:
            raise Exception('"{}" does not identify a problem'.format(slug))

    if request.method == 'POST':
        # Use submitted form to create/update problem info within model
        edit_form = forms.CreateOrEditProblemForm(request.POST, request.FILES)

        if edit_form.is_valid():

            # Get slug first so we can use it to name the file
            slug = slugify(edit_form.cleaned_data['title'])

            # Get list of uploaded files
            myfiles = request.FILES.getlist('testcases')

            # Create tar file containing testcases only if new testcases were
            # uploaded
            testcasepath = settings.MEDIA_ROOT + '/testcase_' + slug + '.tar'
            if len(myfiles):
                with tarfile.open(testcasepath, mode='w|gz') as t:
                    for f in myfiles:
                        path = helpers.store_uploaded_file(f, '/tmp/')
                        t.add(path, arcname=f.name)

            # Get info for problem from form
            problem_info = {
                'slug': slug,
                'author': request.user,
                'title': edit_form.cleaned_data['title'],
                'description': edit_form.cleaned_data['description'],
                'testcases': testcasepath,
                'time_limit': edit_form.cleaned_data['time_limit'],
                'mem_limit': edit_form.cleaned_data['mem_limit'],
                'memswap_limit': edit_form.cleaned_data['memswap_limit'],
                'contest': helpers.get_contest_record(
                    slugify(edit_form.cleaned_data['contest']))
            }

            if problem and slug == problem.slug:
                # Save an updated version of an old problem
                update_fields = ['title', 'description', 'time_limit', 'mem_limit', 'memswap_limit', 'contest']

                if len(myfiles):
                    # User uploaded new testcases
                    update_fields.append('testcases')

                for attr in update_fields:
                    setattr(problem, attr, problem_info[attr])

                problem.save(update_fields=update_fields)
            else:
                # Save a completely new problem
                models.ProblemModel(**problem_info).save()

            return redirect('/problems/' + slug)
    else:
        # Present form to user
        edit_form = forms.CreateOrEditProblemForm(problem_info)

    context = {
        'form': edit_form,
        'nbar': 'Problems'
    }

    return render(request, 'edit.html', context=context)


@login_required
def all_contests(request):
    '''
    Display all contests
    '''
    context = {
        'contests': models.ContestModel.objects.all().order_by('-id'),
        'nbar' : 'Contests'
    }

    return render(request, 'all_contests.html', context=context)


def create_or_edit_contest(request, slug=''):
    '''
    Handle contest creation and editing
    '''
    contest = None
    contest_info = {}
    if slug != '':
        contest = helpers.get_contest_record(slug)
        if contest:
            contest_info = {
                'name': contest.name,
                'start_time': contest.start_time,
                'end_time': contest.end_time
            }
        else:
            raise Exception('"{}" does not identify a problem'.format(slug))
            
    if request.method == 'POST':
        edit_form = forms.CreateOrEditContestForm(request.POST)

        if edit_form.is_valid():

            # Get slug for new contest
            slug = slugify(edit_form.cleaned_data['name'])

            # Extract info from form
            contest_info = {
                'name': edit_form.cleaned_data['name'],
                'slug': slug,
                'start_time': edit_form.cleaned_data['start_time'],
                'end_time': edit_form.cleaned_data['end_time']
            }

            if contest and slug == contest.slug:
                # Save an updated version of an old contest
                update_fields = ['start_time', 'end_time']

                for attr in update_fields:
                    setattr(contest, attr, contest_info[attr])

                contest.save(update_fields=update_fields)
            else:
                # Save completely new contest
                models.ContestModel(**contest_info).save()

            return redirect('/contests')
    else:
        # Present form to user
        edit_form = forms.CreateOrEditContestForm(contest_info)

    context = {
        'form': edit_form,
        'nbar': 'Contests'
    }

    return render(request, 'edit_contest.html', context=context)


def contest(request, slug=''):
    '''
    View and participate in contest
    '''
    return display_problems(request, contest_slug=slug)


def chat(request):

    context = {
        'nbar': 'Chat'
    }

    return render(request, 'chat/chat.html', context=context)

def room(request, room_name):

    context = {
        'nbar': 'Chat',
        'room_name_json': mark_safe(json.dumps(room_name)),
    }

    return render(request, 'chat/room.html', context=context)


def room_headless(request, room_name):

    context = {
        'nbar': 'Chat',
        'room_name_json': mark_safe(json.dumps(room_name)),
    }

    return render(request, 'chat/room_headless.html', context=context)
