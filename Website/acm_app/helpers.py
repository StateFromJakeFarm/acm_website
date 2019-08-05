import os
import re
import requests

from random import random
from time import gmtime
from hashlib import md5

from . import models

def store_uploaded_file(posted_file, local_dir):
    '''
    Save a POST'ed file locally on the server and return path to local
    version of file
    '''
    # Use unique file name to avoid race condition where simultaneous
    # submissions with same file name clobber each other
    unique_name = gen_unique_str() + posted_file.name

    # Write solution file to disk
    local_file_path = os.path.join(local_dir, unique_name)
    with open(local_file_path, 'wb+') as dest:
        for chunk in posted_file.chunks():
            # Write in chunks so whole file doesn't get loaded into memory all
            # at once if it's really big
            dest.write(chunk)

    return local_file_path

def run_submission(submission_path, testcases_path, time_limit):
    '''
    Send POST request to grader container to make it run submitted code
    '''
    payload = {
        'submission': submission_path,
        'testcases': testcases_path,
        'time_limit': time_limit
    }
    r = requests.post('http://grader:5000', data=payload)

    # Get results from code runner and determine if problem was solved
    text = r.content.decode('utf-8').strip()
    passed = re.search('(Failed)|(Error)|(Timeout)', text) is None

    result = {
        "text" : text,
        "result" : passed
    }

    return result

def user_has_already_solved_problem(user_obj, problem_obj):
    '''
    Return True if a user has already solved a problem
    '''
    return (len(models.UserSolvedProblems.objects.filter(user=user_obj,
        problem=problem_obj)) > 0)

def get_problem_record(slug):
    '''
    Return reference to problem model instance identified by given slug or
    None if problem doesn't exist
    '''
    problem_queryset = models.ProblemModel.objects.filter(slug=slug)

    return (problem_queryset[0] if len(problem_queryset) else None)

def get_contest_record(slug):
    '''
    Return reference to contest model instance identified by given slug or
    None if contest doesn't exist
    '''
    contest_queryset = models.ContestModel.objects.filter(slug=slug)

    return (contest_queryset[0] if len(contest_queryset) else None)

def is_participant(contest_obj, user_obj):
    '''
    Return true if user is a participant in given contest, false otherwise
    '''
    return bool(len(contest_obj.participants.filter(user=user_obj)))

def gen_unique_str():
    '''
    Generate a unique string using the MD5 hash algo
    '''
    rand_str = str(random())
    hash_obj = md5()
    hash_obj.update(rand_str.encode('utf-8'))

    return hash_obj.hexdigest()

def get_contest_choices():
    '''
    Return list of tuples used to select contest in problem edit form
    '''
    return [('', '')] + [(c.name, c.name) for c in models.ContestModel.objects.all()]
