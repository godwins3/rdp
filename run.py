from scripts import db
from scripts.models import User, Post
from app import *

@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Post": Post}
