import os
import requests

def store_uploaded_file(posted_file, local_dir):
    '''
    Save a POST'ed file locally on the server and return path to local
    version of file
    '''
    local_file_path = os.path.join(local_dir, posted_file.name)
    with open(local_file_path, 'wb+') as dest:
        for chunk in posted_file.chunks():
            # Write in chunks so whole file doesn't get loaded into memory all
            # at once if it's really big
            dest.write(chunk)

    return local_file_path

def run_submission(file_path):
    '''
    Send POST request to grader container to make it run submitted code
    '''
    payload = {'file_path': file_path}
    r = requests.post('http://0.0.0.0:5000', data=payload)

    return r.content
