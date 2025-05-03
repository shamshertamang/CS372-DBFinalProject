# auth.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .database import get_user_by_email, create_user, get_user_by_username
import re


"""
This script contains method for login and sign up. This was taken and adapted from techwithtim's flask tutorial which is cited in the README'

The password in these methods down below are not hashed in order to support dml.sql. to use the app for actual use you need to uncomment
line 33 and line 78 and remove line 79
"""


auth = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = get_user_by_email(email)

        if user:
            # if check_password_hash(user.password, password):
            if user.password == password:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        user_name = request.form.get('userName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not is_valid_email(email):
            flash('Invalid email format.', category='error')
            return redirect(url_for('auth.sign_up'))
        if get_user_by_username(user_name):
            flash('Username already in use.', category='error')
            return redirect(url_for('auth.sign_up'))

        existing_user = get_user_by_email(email)
        if existing_user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(user_name) < 2:
            flash('User name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # hashed_password = generate_password_hash(password1, method='scrypt')
            hashed_password = password1
            new_user = create_user(email = email, user_name=user_name, password=hashed_password)
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

