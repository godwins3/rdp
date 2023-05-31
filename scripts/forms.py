# -*- coding: utf-8 -*-

from wtforms import Form, StringField, validators, SubmitField, TextAreaField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
    username = StringField('Username:', validators=[validators.Length(min=1, max=30)])
    password = StringField('Password:', validators=[validators.Length(min=1, max=30)])
    email = StringField('Email:', validators=[validators.optional(), validators.Length(min=0, max=50)])

class ContactForm(Form):
    name = StringField('Name:', validators=[validators.optional(), validators.Length(min=0, max=50)])
    email = StringField('Email:', validators=[validators.optional(), validators.Length(min=0, max=50)])
    phone = StringField('Phone:', validators=[validators.optional(), validators.Length(min=0, max=13)])
    message = StringField('Message:', validators = [validators.optional(), validators.Length(min=0, max=300)])

class PostForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired("Required field!"),
            Length(
                min=3,
                max=120,
                message="Make sure the title is between 3 and 120 characters.",
            ),
        ],
    )
    description = TextAreaField(
        "Description",
        validators=[
            Length(
                max=240,
                message="Make sure the description field is no longer than 240 characters.",
            )
        ],
    )
    body = TextAreaField("Content", validators=[DataRequired("Required field!")])
    image = FileField(
        "Cover Article", validators=[FileAllowed(["jpg", "jpeg", "png"])]
    )
    submit = SubmitField("Publish Post")
