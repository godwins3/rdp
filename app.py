# -*- coding: utf-8 -*-

from scripts import tabledef
from scripts import forms
from scripts.forms import PostForm
from scripts.utils import save_picture, title_slugifier
from scripts import helpers
from scripts.models import Post, user
from flask import Flask, redirect, url_for, render_template, request, session, abort, flash
from flask_login import login_required, current_user
import json
import sys
import os
from . import app, db

app = Flask(__name__)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only

# Heroku
#from flask_heroku import Heroku
#heroku = Heroku(app)

# ======== Routing =========================================================== #
# -------- Index ------------------------------------------------------------- #
@app.route('/', methods=['GET'])
def home():
    title = 'rdp - Home'
    return render_template('index.html', title=title)

# -------- Login ------------------------------------------------------------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    title = 'rdp - Login'
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if helpers.credentials_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both fields required'})
        return render_template('login.html', form=form)
    user = helpers.get_user()
    return render_template('index.html', user=user, title=title)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


# -------- Signup ---------------------------------------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    title = 'rdp - signup'
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'User/Pass required'})
        return render_template('login.html', form=form, title=title)
    return redirect(url_for('login'))


# -------- Settings ---------------------------------------------------------- #
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.change_user(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))

@app.route('/about')
def about():
    title ="rdp - about"
    return render_template('about.html', title=title)

@app.route('/events')
def events():
    title ="rdp - events"
    if not session.get('logged_in'):
        
        return render_template('events.html', title=title)
    
    return redirect(url_for('login'))
@app.route("/index")
def homepage():
    page_number = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page_number, 6, True)

    if posts.has_next:
        next_page = url_for("homepage", page=posts.next_num)
    else:
        next_page = None

    if posts.has_prev:
        previous_page = url_for("homepage", page=posts.prev_num)
    else:
        previous_page = None

    return render_template(
        "homepage.html",
        posts=posts,
        current_page=page_number,
        next_page=next_page,
        previous_page=previous_page,
    )


@app.route("/posts/<string:post_slug>")
def post_detail(post_slug):
    post_instance = Post.query.filter_by(slug=post_slug).first_or_404()
    return render_template("post_detail.html", post=post_instance)


@app.route("/create-post", methods=["GET", "POST"])
@login_required
def post_create():
    form = PostForm()
    if form.validate_on_submit():
        slug = title_slugifier(form.title.data)
        new_post = Post(
            title=form.title.data,
            body=form.body.data,
            slug=slug,
            description=form.description.data,
            author=current_user,
        )

        if form.image.data:
            try:
                image = save_picture(form.image.data)
                new_post.image = image
            except Exception:
                db.session.add(new_post)
                db.session.commit()
                flash(
                    "There was a problem uploading the image. Change image and try again."
                )
                return redirect(url_for("post_update", post_id=new_post.id))

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("post_detail", post_slug=slug))
    return render_template("post_editor.html", form=form)


@app.route("/posts/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def post_update(post_id):
    post_instance = Post.query.get_or_404(post_id)
    if post_instance.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post_instance.title = form.title.data
        post_instance.description = form.description.data
        post_instance.body = form.body.data

        if form.image.data:
            try:
                image = save_picture(form.image.data)
                post_instance.image = image
            except Exception:
                db.session.commit()
                flash(
                    "There was a problem uploading the image. Change image and try again."
                )
                return redirect(url_for("post_update", post_id=post_instance.id))

        db.session.commit()
        return redirect(url_for("post_detail", post_slug=post_instance.slug))
    elif request.method == "GET":
        form.title.data = post_instance.title
        form.description.data = post_instance.description
        form.body.data = post_instance.body

    post_image = post_instance.image or None
    return render_template("post_editor.html", form=form, post_image=post_image)


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
@login_required
def post_delete(post_id):
    post_instance = Post.query.get_or_404(post_id)
    if post_instance.author != current_user:
        abort(403)
    db.session.delete(post_instance)
    db.session.commit()
    return redirect(url_for("homepage"))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    title = 'rdp - contact us'
    form = forms.ContactForm(request.form)
    if request.method == 'GET':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        phone = request.form['phone']
        return "Form posted. name: {}, email:{}, message:{}, phone:{}".format(name, email, message, phone)
    return render_template('contact.html', form=form, title=title)

#---------------- error handling ------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(401)
def unauthorized_error(error):
    return render_template("401.html"), 401

# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host="0.0.0.0")
