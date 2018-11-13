from flask import Flask
import docker

app = Flask(__name__)

client = docker.from_env()

@app.route("/")
def hello():
    container = client.containers.create("acm_website_runner", auto_remove=True)
    f = open("test.tar").read()
    container.put_archive("/code", f)
    container.start()
    logs = container.logs()
    container.kill()
    return logs

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
