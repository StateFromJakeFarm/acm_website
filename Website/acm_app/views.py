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
from django.utils import timezone

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


def display_problems(request, contest=None):
    '''
    Display all problems
    '''
    if contest:
        # Grab all problems from requested contest
        problems = models.ProblemModel.objects.filter(contest=contest).order_by('-id')
    else:
        # Grab all problems not belonging to any contest
        problems = models.ProblemModel.objects.filter(contest=None).order_by('-id')

    context = {
        'problems': problems,
        'nbar' : 'Contests' if contest else 'Problems',
    }

    if contest:
        # Add contest name and slug
        context.update({'contest_name': contest.name, 'contest_slug': contest.slug})

    return render(request, 'problem/display.html', context=context)


def problem(request, slug=''):

    # Get problem object from database
    problem = helpers.get_problem_record(slug)
    if not problem:
        raise Exception('"{}" does not identify a problem'.format(slug))

    text_results = ''

    if request.method == 'POST':
        # Record timestamp at time of submission so we can get time-to-solve
        # penalty if this is for a competition
        submission_timestamp = timezone.now()

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

            if not helpers.user_has_already_solved_problem(request.user, problem):
                participant_entry = models.ParticipantModel.objects.get(user=request.user)
                if boolean_result:
                    if problem.contest:
                        # Update user's competition score and add time-to-solve penalty
                        participant_entry.score = F('solved') + 1

                        time_delta = (submission_timestamp - problem.contest.start_time).total_seconds()
                        participant_entry.penalty = F('penalty') + time_delta
                        participant_entry.update()

                    # update leaderboard if solved
                    # verify correctness and award a point if winner
                    leaderboard_entry = models.LeaderboardModel.objects.get(user=request.user)
                    leaderboard_entry.score = F('score') + 1 # F is atomic or something and avoids race condition
                    leaderboard_entry.save()

                    # Record that user has solved this problem
                    solved_problem_entry = models.UserSolvedProblems(user=request.user, problem=problem)
                    solved_problem_entry.save()
                elif problem.contest:
                    # Incorrect contest problem submission; add penalty
                    participant_entry.penalty = F('penalty') + 1200 # (20 mins)
                    participant_entry.update()

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

        return render(request, 'problem/problem.html', context=context)


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
            }

            if problem.contest:
                # This problem is part of a contest
                problem_info['contest'] = problem.contest.name
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

    return render(request, 'problem/edit.html', context=context)


@login_required
def display_contests(request):
    '''
    Display all contests
    '''
    context = {
        'contests': models.ContestModel.objects.all().order_by('-id'),
        'nbar' : 'Contests'
    }

    return render(request, 'contest/display.html', context=context)


@login_required
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
            raise Exception('"{}" does not identify a contest'.format(slug))
            
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

    return render(request, 'contest/edit.html', context=context)


@login_required
def contest(request, slug=''):
    '''
    View contest problems or redirect to registration page
    '''
    contest = helpers.get_contest_record(slug)
    if helpers.is_participant(contest, request.user):
        return display_problems(request, contest)
    else:
        return redirect('/contests/' + slug + '/register')


@login_required
def contest_register(request, slug=''):
    '''
    Allow user to register for a contest
    '''

    # Grab contest
    contest = helpers.get_contest_record(slug)

    if request.method == 'POST':
        # Create participant record for this user if one doesn't already exist
        if not len(contest.participants.filter(user=request.user)):
            participant = models.ParticipantModel(user=request.user)
            participant.save()
            contest.participants.add(participant)

        return redirect('/contests/' + slug + '/problems')

    context = {
        'contest_name': contest.name,
        'start_time': contest.start_time,
        'end_time': contest.end_time
    }

    return render(request, 'contest/register.html', context=context)


def scoreboard(request, slug=''):
    '''
    Display scoreboard for specific contest
    '''
    contest = helpers.get_contest_record(slug)
    context = {
        'participants': contest.participants.all().order_by('solved'),
        'contest_name': contest.name,
        'contest_slug': contest.slug
    }

    return render(request, 'contest/scoreboard.html', context=context)


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
