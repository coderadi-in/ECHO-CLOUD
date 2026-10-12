"""
Auth specific api routes management file for the Project.

Manages the routes of AUTH specific api.
"""

# ==================================================
# SETUP
# ==================================================

# ? IMPORTS
from flask import Blueprint, jsonify, request, send_file
from plugins import *
from models import *
from functools import wraps

# | ROUTER INIT
auth = Blueprint('auth', __name__, url_prefix='/api/auth')

# | AUXILIARY REFERENCES
today = date.today()

# & DECORATOR FOR CHECKING AUTHENTICATION
def admin_authentication_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        admin_id = request.headers.get('admin-id')
        admin_key = request.headers.get('admin-key')

        if (not admin_id) or (admin_id != os.getenv("ADMIN_ID")):
            return jsonify({
                "status": 401,
                "message": "Admin ID is missing or is invalid."
            }), 401
        
        if (not admin_key) or (admin_key != os.getenv("ADMIN_KEY")):
            return jsonify({
                "status": 403,
                "message": "You have admin ID but you need a specific admin KEY to get admin access."
            }), 403
        
        return func(*args, **kwargs)

    return wrapper

# ==================================================
# END-POINTS
# ==================================================

# & CREATE NEW USER
@auth.route('/register', methods=['POST'])
@limiter.limit("30 per minute")
def register_user():
    # ACCESS JSON DATA
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    site_url = data.get('site_url')
    current_plan = data.get('current_plan')

    # CHECK FOR EXISTING USER WITH SAME EMAIL
    if (User.query.filter_by(email=email).first()):
        return jsonify({
            "status": 400,
            "error": "UserAlreadyExistsError",
            "message": "User already exists with same email.",
            "details": None
        }), 400

    # FETCH AUXILIARY DETAILS
    plan_info = ACCOUNT_PLANS.get(current_plan.lower())
    if (not plan_info):
        return jsonify({
            "status": 404,
            "error": "PlanNotFoundError",
            "message": f"No plan found named {current_plan}",
            "details": None
        }), 404

    # CREATE NEW USER OBJECT
    new_user = User(
        name=name,
        email=email,
        password=encoder.generate_password_hash(password),
        site_url=site_url,
        current_plan=plan_info.get('plan_name'),
        total_credits=plan_info.get('credits'),
        left_credits=plan_info.get('credits'),
    )

    # ADD USER OBJECT TO DB ROW
    db.session.add(new_user)
    db.session.commit()

    # RETURN RESPONSE
    return jsonify({
        "status": 200,
        "error": None,
        "message": "User added successfully!",
        "details": {
            "name": new_user.name,
            "email": new_user.email,
            "site_url": new_user.site_url,
            "current_plan": new_user.current_plan,
            "total_credits": new_user.total_credits,
        }
    }), 200


# & AUTHENTICATE USER AND START SESSION
@auth.route('/login', methods=['POST'])
@limiter.limit("30 per minute")
def login_user():
    # ACCESS JSON DATA
    data = request.json
    userid = data.get('userid')

    # VALIDATE DATA
    if (not user) or (not userid.isdigit()):
        return jsonify({
            "status": 400,
            "error": "ValueError",
            "message": f"User id [{userid}] is invalid.",
            "details": None
        }), 400

    user = User.query.get(int(userid))

    # VALIDATE USER
    if (not user):
        return jsonify({
            "status": 404,
            "error": "UserNotFoundUser",
            "message": f"User [user-{userid}] not found.",
            "details": { "userid": userid, }
        }), 404

    # MAIN BODY
    login_user(user)

    # RETURN RESPONSE
    return jsonify({
        "status": 200,
        "error": None,
        "message": "User logged in successfully!",
        "details": {
            "userid": userid,
            "name": user.name,
        }
    }), 200


# & END USER SESSION
@auth.route('/logout', methods=['POST'])
@limiter.limit("30 per minute")
def logout_user():
    # ACCESS JSON DATA
    data = request.json
    userid = data.get('userid')

    # VALIDATE DATA
    if (not userid) or not (userid.isdigit()):
        return jsonify({
            "status": 400,
            "error": "UserNotFoundError",
            "message": f"User [user-{userid}] not found.",
            "details": { "userid": userid, }
        }), 400


# & RETURN/UPDATE CURRENT AUTHENTICATED USER PROFILE
@auth.route('/me', methods=['GET', 'PATCH'])
@limiter.limit("30 per minute")
def me():
    if (request.method == 'GET'):
        return jsonify({
            "status": 200,
            "error": None,
            "message": None,
            "user": current_user,
            "details": None,
            "authenticated": current_user.is_authenticated
        }), 200

    elif (request.method == 'PATCH'):
        # ACCESS JSON DATA
        data = request.json
        name = data.get('name', current_user.name)
        email = data.get('email', current_user.email)
        new_password = data.get('new_password')
        old_password = data.get('old_password')
        site_url = data.get('site_url', current_user.site_url)

        # UPDATE DATA
        current_user.name = name
        current_user.email = email
        current_user.site_url = site_url

        # PASSWORD DATA VALIDATION
        if (not new_password) or (not old_password):
            return jsonify({
                "status": 400,
                "error": "PasswordNotMatchedError",
                "message": "Either new password or old password is missing.",
                "details": {
                    "new_password": new_password,
                    "old_password": old_password,
                }
            }), 400

        # PASSWORD VALUE VALIDATION
        if (not encoder.check_password_hash(current_user.password, old_password)):
            return jsonify({
                "status": 400,
                "error": "PasswordNotMatchedError",
                "message": "Invalid password.",
                "details": {
                    "new_password": new_password,
                    "old_password": old_password,
                }
            }), 400

        # UPDATE PASSWORD AND UPDATE DB
        current_user.password = encoder.generate_password_hash(new_password)
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            "status": 200,
            "error": None,
            "message": "Profile updated successfully.",
            "details": {
                "name": name,
                "email": email,
                "site_url": site_url,
            }
        })


