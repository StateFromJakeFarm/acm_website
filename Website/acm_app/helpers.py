import os
import requests

from hashlib import md5
from random import randrange

def store_uploaded_file(posted_file, local_dir):
    '''
    Save a POST'ed file locally on the server and return path to local
    version of file
    '''
    # Use unique file name to avoid race condition where simultaneous
    # submissions with same file name clobber each other
    hash_obj = md5()
    hash_obj.update(str(randrange(1337)).encode('utf-8'))
    unique_name = hash_obj.hexdigest() + posted_file.name

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
    r = requests.post('http://backend:5000', data=payload)

    return r.content
