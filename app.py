import os
import json

import requests
from flask import Flask, render_template, jsonify, request
from gist import GistAPI

app = Flask(__name__)

try:
    app.config.from_object('config')
except ImportError:
    pass

if "GITHUB_API_TOKEN" in os.environ:
    app.config.update(GITHUB_API_TOKEN=os.environ["GITHUB_API_TOKEN"])


api = GistAPI(app.config["GITHUB_API_TOKEN"])


@app.route("/")
def editor():
    return render_template("editor.html")


@app.route("/help/")
def help():
    return render_template("help.html")

@app.route("/create/<file_name>/", methods=["POST"])
def create(file_name):
    content = request.get_json()["content"]
    html_url = api.create(
        desc="Gist containing micro python micro:bit code",
        public=True,
        files={file_name: {"content": content}})
    gist_id = html_url.split("/").pop()
    return jsonify(id=gist_id), 201

@app.route("/load/<gist_id>/<file_name>/")
def load(gist_id, file_name):
    content = api.content(gist_id)[file_name]
    return jsonify(content=content)


@app.route("/save/<gist_id>/<file_name>", methods=["POST"])
def save(gist_id, file_name):
    content = request.get_json()["content"]
    # We have to call this request manually because the gist api assumes that
    # edits happen in the terminal (e.g. using vim) and are then git pushed
    # back to GitHub. This isn't true in our case :(
    req = requests.Request(
        "PATCH",
        "https://api.github.com/gists",
        headers={
            "Accept-Encoding": "identity, deflate, compress, gzip",
            "User-Agent": "python-requests/1.2.0",
            "Accept": "application/vnd.github.v3.base64",
        },
        params={'access_token': api.token},
        data=json.dumps({
            "files": {file_name: {
                "content": content
            }}
        })
    )
    api.send(req, gist_id)
    return jsonify(status="OK")


if __name__ == "__main__":
    app.run(debug=True)
