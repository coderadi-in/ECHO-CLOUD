"""
Legal consent routes management file for the Project.

Manages the legal consent related routes.
"""

# ? IMPORTS
from flask import Blueprint, render_template

# ! ROUTER INIT
legal = Blueprint("legal", __name__, url_prefix='/legal')

# & PRIVACY POLICY ROUTE
@legal.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')

# & TERMS OF SERVICE ROUTE
@legal.route('/terms')
def terms():
    return render_template('legal/terms.html')