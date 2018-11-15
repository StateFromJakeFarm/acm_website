import sys
import docker
import tarfile

from flask import Flask, request

app = Flask(__name__)

client = docker.from_env()

@app.route("/", methods=['POST'])
def run_submission():
    # Create tar file containing submission
    with tarfile.open('test.tar', mode='w|gz') as t:
        t.add(request.form.get('file_path'))

    # Create container and copy archive containing submission over to it
    container = client.containers.create('acm_website_runner', auto_remove=True)
    container.put_archive('/code', open('test.tar', 'rb').read())

    # Start container and record its logs
    container.start()
    logs = container.logs()
    try:
        container.kill()
    except:
        print('Could not kill code runner container!', file=sys.stderr)
        
    return logs

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
