from flask import Flask
from scripts.models import User, Post
app = Flask(__name__)

@app.shell_context_processor
def make_shell_context():
    return { "User": User, "Post": Post}
