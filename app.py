# -*- coding: utf-8 -*-

from scripts import tabledef
from scripts import forms
from scripts import helpers
from flask import Flask, redirect, url_for, render_template, request, session
import json
import sys
import os

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
    return render_template('home.html', user=user, title=title)


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
    if session.get('logged_in'):
        return render_template('events.html', title=title)
    return redirect(url_for('login'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    title = 'rdp - contact us'
    form = forms.ContactForm(request.form)
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        phone = form.phone.data
        return "Form posted. name: {}, email:{}, message:{}, phone:{}".format(name, email, message, phone)
    return render_template('contact.html', form=form, title=title)
# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host="0.0.0.0")
