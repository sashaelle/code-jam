from flask import Flask, render_template, request
from markupsafe import escape

app = Flask(__name__)

@app.route("/hello")
def hello_world():
    return "<p>Hello World!</p>"

@app.route("/")
def index():
    return render_template('render.html')

@app.route("/user/<name>")
def user(name):
    return f'Hello {escape(name)}!'
