from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def editor():
    return render_template("editor.html")


@app.route("/help/")
def help():
    return render_template("help.html")


if __name__ == "__main__":
    app.run(debug=True)
