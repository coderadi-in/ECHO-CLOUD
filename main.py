"""
Main file of the Project.

Binds everything at one place.
"""

# ==================================================
# ENVIRONMENT & SSL SETUP
# ==================================================

# ! SETUP MONKEY PATCH
import gevent.monkey
gevent.monkey.patch_all()

# ! LOAD VENV
from dotenv import load_dotenv
load_dotenv('.venv/vars.env')

# ==================================================
# BINDING SETUP
# ==================================================

# ? IMPORTS
from flask import Flask, render_template, redirect, url_for, flash
from plugins import *
from routers import *
from apis import *
from models import *
import socket_listeners

# ! SERVER INIT
server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config['SECRET_KEY'] = os.getenv("SEC_KEY")
server.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
server.config['SESSION_PERMANENT'] = True

# ==================================================
# PLUGINS AND DATABASE
# ==================================================

# & EXTENSIONS BINDING
bind_plugins(server)
bind_routers(server)
bind_apis(server)

# & DATABASE & LOGGING INIT
with server.app_context():
    if (not os.path.exists('migrations')): init_migrator()
    db.create_all()
    init_logging_setup()

# ==================================================
# AUTHENTICATION AND ROUTE REDIRECTION
# ==================================================

# | USER LOADER
@logger.user_loader
def load_user(user):
    return User.query.get(user)

# | BASE ROUTE
@server.route('/')
def index():
    if (current_user.is_authenticated):
        return redirect(url_for("app.dashboard"))
    return render_template("index.html")

# ==================================================
# ERROR HANDLES
# ==================================================

# & UNAUTHORIZED
@server.errorhandler(401)
def handle_401(error):
    flash("Login required", "error")
    return redirect('/')

# # & BAD REQUEST
# @server.errorhandler(400)
# def handle_400(error = None):
#     flash("Something went wrong on our side!", "error")
#     return redirect('/')

# & NOT FOUND
@server.errorhandler(404)
def handle_404(error = None):
    return render_template('err/404.html')

# & TOO MANY REQUESTS
@server.errorhandler(429)
def handle_429(error = None):
    logout_user()
    flash("Too many requests from your side.", "error")
    return redirect('/')

# & INTERNAL SERVER ERROR
@server.errorhandler(500)
def handle_500(error):
    return render_template("err/500.html")