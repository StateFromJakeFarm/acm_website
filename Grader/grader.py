import os
import sys
import time
import docker
import tarfile

from flask import Flask, request

app = Flask(__name__)

client = docker.from_env()

@app.route("/", methods=['POST'])
def run_submission():
    # Create tar file containing submission
    with tarfile.open('submission.tar', mode='w|gz') as t:
        t.add(request.form.get('submission'))

    # Set environment variables so container knows how to navigate all the files
    # it's received
    environment = {
        'SUBMISSION_FILE': request.form.get('submission')[1:],
        'TIME_LIMIT': request.form.get('time_limit')
    }

    # Create container
    container = client.containers.create('acm_website_runner', environment=environment)

    # Put testfiles and submssion in as archives
    container.put_archive('/code/tests', open(request.form.get('testcases'), 'rb').read())
    container.put_archive('/code', open('submission.tar', 'rb').read())

    # Start container and record its logs
    container.start()

    # Block function until container finishes running (may want timeout in future)
    container.wait()

    # Get container logs
    logs = container.logs()
    try:
        container.remove()
    except:
        print('Could not remove code runner container!', file=sys.stderr)

    return logs

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
