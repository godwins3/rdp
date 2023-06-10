# -*- coding: utf-8 -*-
import sqlite3
from scripts import tabledef
from scripts import forms, db
from scripts.forms import PostForm
from scripts.utils import save_picture, title_slugifier
from scripts import helpers
from scripts.models import Post, User
from flask import Flask, redirect, url_for, render_template, request, session, abort, flash
from flask_login import login_required, current_user
import smtplib
import json
import sys
import os
from app import *

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
def join_us():
    title = 'rdp - Login'
    return render_template('index.html', title=title)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


# -------- Signup ---------------------------------------------------------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    title = 'rdp - signup'  
    form = forms.LoginForm(request.form)
    if request.method == 'POST':
        surname = request.form['surname'].upper()
        othername = request.form['othername'].upper()
        mobile = request.form['mobile']
        idnumber = request.form['idnumber']
        D_O_B = request.form['D_O_B']
        gender = request.form['gender'].upper()
        county = request.form['county'].upper()
        constituency = request.form['constituency'].upper()
        email = request.form['email']
        if not helpers.id_taken(idnumber):
            helpers.add_user(                        
                    email, 
                    surname, 
                    othername,
                    mobile,
                    idnumber,
                    D_O_B,
                    gender,
                    county,
                    constituency
                    )
            form =forms.LoginForm(request.form)
            return json.dumps({'status': 'Registration successful'})
        return json.dumps({'status': 'id taken'})
    else:
        form =forms.LoginForm(request.form)
    return render_template('login.html', form=form, title=title)
    

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

@app.route('/leadership')
def leadership():
    title ="rdp - our leaders"
    return render_template('leadership.html', title=title)

@app.route('/events')
def events():
    title ="rdp - events"
    return render_template('events.html', title=title)

def send_email(name, email, message):
    # Set up the SMTP server details
    smtp_server = 'smtp.example.com'
    smtp_port = 587
    smtp_username = 'your_username'
    smtp_password = 'your_password'
    admin_email = 'admin@admin.com'
    
    # Compose the email message
    subject = 'New Contact Form Submission'
    body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    message = f"Subject: {subject}\n\n{body}"
    
    try:
        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            
            # Send the email
            server.sendmail(email, admin_email, message)
    
    except Exception as e:
        print(f"Error sending email: {str(e)}")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle the form submission here (e.g., send an email)
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # Add your code to handle the form data
        
        # Send email to admin
        send_email(name, email, message)
    else:
        return render_template('contact.html')
    
# ---------- admin ------------------------------------------------------------------------------------

# Hard-coded admin login details
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

# Endpoint for admin dashboard login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Successful login, redirect to the admin dashboard
            return redirect('/admin/dashboard')
        else:
            return 'Invalid login credentials'
    
    return render_template('admin_login.html')

# Endpoint for admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    registered_users = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', users=registered_users)


#---------------- error handling ------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(401)
def unauthorized_error(error):
    return render_template("401.html"), 401

# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=8000)
