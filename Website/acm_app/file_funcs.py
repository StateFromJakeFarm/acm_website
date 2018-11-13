import os

def store_uploaded_file(posted_file, local_dir):
    '''Save a POST'ed file locally on the server'''
    with open(os.path.join(local_dir, posted_file.name), 'wb+') as dest:
        for chunk in posted_file.chunks():
            # Write in chunks so whole file doesn't get loaded into memory all
            # at once if it's really big
            dest.write(chunk)
