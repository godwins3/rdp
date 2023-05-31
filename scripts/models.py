from datetime import datetime

from . import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    title = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(250))
    description = db.Column(db.String(240))
    body = db.Column(db.Text(), nullable=False)
    image = db.Column(db.String(120))

    def __repr__(self):
        return f"Post('{ self.id }', '{ self.title }')"
