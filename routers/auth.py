"""
Application authorization routes management file for the Project.

Manages the auth related routes.
"""

# ? IMPORTS
from flask import Blueprint, redirect, url_for, flash, request
from models import *
from plugins import *

# ! ROUTER INIT
auth = Blueprint("auth", __name__, url_prefix='/auth')

# & SIGNUP ROUTE
@auth.route('/signup', methods=['POST'])
@limiter.limit("30 per minute")
def signup():
    # ACCESS FORM DATA
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    # FORM VALIDATION
    if (not name) or (not email) or (not password):
        flash("One or more required fields aren't filled.", "error")
        return redirect('/')
    
    # EMAIL VALIDATION
    if (User.query.filter_by(email=email).first() is not None):
        flash("The provided email is already linked with an ECHO account.", "error")
        return redirect('/')
    
    # ADD USER TO DATABASE
    new_user = User(
        name=name,
        email=email,
        password=encoder.generate_password_hash(password).decode('utf-8')
    )

    db.session.add(new_user)
    db.session.commit()

    # LOGIN AND REDIRECT
    login_user(new_user, remember=True)
    flash("Logged in! Welcome to ECHO.", "waving_hand")
    return redirect(url_for('app.dashboard'))

# & LOGIN ROUTE
@auth.route('/login', methods=['POST'])
@limiter.limit("30 per minute")
def login():
    # ACCESS FORM DATA
    email = request.form.get('email')
    password = request.form.get('password')

    # FORM VALIDATION
    if (not email) or (not password):
        flash("One or more required fields aren't filled.", "error")
        return redirect('/')
    
    # EMAIL VALIDATION
    logged_user = User.query.filter_by(email=email).first()
    if (logged_user is None):
        flash("The provided email is not linked with any ECHO account.", "error")
        return redirect('/')
    
    # PASSWORD VALIDATION
    if (not encoder.check_password_hash(logged_user.password, password)):
        flash("Password mismatched!", "error")
        return redirect('/')
    
    # LOGIN AND REDIRECT
    login_user(logged_user, remember=True)
    flash("Logged in! Welcome to ECHO.", "waving_hand")
    return redirect(url_for('app.dashboard'))

# & LOGOUT ROUTE
@auth.route('/logout')
@limiter.limit("30 per minute")
def logout():
    logout_user()
    flash("You account has been logged out.", "info")
    return redirect('/')