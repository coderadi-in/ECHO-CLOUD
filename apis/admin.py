"""
Application admin api routes management file for the Project.

Manages the routes of admin api.
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
admin = Blueprint('admin', __name__, url_prefix='/api/admin')

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
                "message": "Admin ID & Key are missing or is invalid."
            }), 401
        
        if (not admin_key) or (admin_key != os.getenv("ADMIN_KEY")):
            return jsonify({
                "status": 403,
                "message": "Admin ID & Key are missing or is invalid."
            }), 403
        
        return func(*args, **kwargs)

    return wrapper

# ==================================================
# ENDPOINTS
# ==================================================

# & LIST ALL USERS
@admin.route('/users')
@admin_authentication_required
@limiter.limit("30 per minute")
def list_users():
    return jsonify({
        'status': 200,
        'error': None,
        'message': None,
        'details': None,
        'output_obj': [u.to_dict() for u in User.query.all()],
    }), 200


# & GET/PATCH/DELETE SPECIFIC USER DETAILS
@admin.route('/users/<id>', methods=['GET', 'PATCH', 'DELETE'])
@admin_authentication_required
@limiter.limit("30 per minute")
def crud_user(id):
    # DATA VALIDATION
    if (not id):
        return jsonify({
            'status': 400,
            'error': 'InvalidIdError',
            'message': f'The id [{id}] is invalid.',
            'details': None,
        }), 400

    user = User.query.get(id)
    if (not user):
        return jsonify({
            'status': 404,
            'error': 'UserNotFoundError',
            'message': f'User [user-{id}] not found.',
            'details': None,
        }), 404

    if (request.method == 'GET'):
        return jsonify({
            'status': 200,
            'error': None,
            'message': None,
            'details': {
                'name': user.name,
                'email': user.email,
                'site_url': user.site_url,
                'total_credits': user.total_credits,
                'left_credits': user.left_credits,
                'last_plan': user.last_plan,
                'current_plan': user.current_plan,
                'renewal_date': user.renewal_date,
            },
            'output_obj': user.to_dict()
        }), 200

    if (request.method == 'PATCH'):
        # ACCESS JSON DATA
        data = request.json
        name = data.get('name', user.name)
        email = data.get('email', user.email)
        site_url = data.get('site_url', user.site_url)
        total_credits = data.get('total_credits', user.total_credits)
        left_credits = data.get('left_credits', user.left_credits)
        last_plan = data.get('last_plan', user.last_plan)
        current_plan = data.get('current_plan', user.current_plan)
        renewal_date = data.get('renewal_date')

        # PROCESS JSON DATA
        total_credits = int(total_credits) if total_credits else 0
        left_credits = int(left_credits) if left_credits else 0
        renewal_date = datetime.strptime(renewal_date, "%Y-%m-%d").date() if renewal_date else user.renewal_date

        # UPDATE USER ROW AND DB
        user.name = name
        user.email = email
        user.site_url = site_url
        user.total_credits = total_credits
        user.left_credits = left_credits
        user.last_plan = last_plan
        user.current_plan = current_plan
        user.renewal_date = renewal_date
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            'status': 200,
            'error': None,
            'message': 'User updated successfully!',
            'details': None,
        }), 200

    else:
        # FUNCTION TO DELETE A LIST FROM DATABASE
        def _delete_from_list(list_: list):
            for data in list_:
                db.session.delete(data)
        
        # DELETE ACCOUNT
        _delete_from_list(user.captions)
        _delete_from_list(user.headlines)
        _delete_from_list(user.barcode_sheets)
        _delete_from_list(user.saved)
        _delete_from_list(user.payments)
        _delete_from_list(user.orders)
        _delete_from_list(user.products)

        # CLOSE DB SESSION
        db.session.delete(user)
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            'status': 200,
            'error': None,
            'message': 'User can their corresponding information has been deleted entirely forever.',
            'details': None,
        }), 200


# & DOWNLOAD LOGS
@admin.route('/logs/download')
@admin_authentication_required
@limiter.limit("30 per minute")
def download_logs():
    # ACCESS LOG TYPE & CORRESPONDING FILE
    log_type = request.args.get('log_type')
    ALLOWED_LOGS = {"errors"}

    if (log_type not in ALLOWED_LOGS):
        return jsonify({
            "status": 400,
            "error": "InvalidLogTypeError",
            "message": f"log_type must be one of {sorted(ALLOWED_LOGS)}.",
            "details": None,
        }), 400

    file_path = os.path.join(current_app.root_path, "logs", f"{log_type}.log")

    # LOG FILE VALIDATION
    if (not os.path.exists(file_path)):
        return jsonify({
            "status": 404,
            "error": "FileNotFoundError",
            "message": "The file doesn't exists in the application directory",
            "details": None
        }), 404

    # RETURN RESPONSE
    return send_file(
        file_path,
        download_name=f"{log_type}.log",
        mimetype="text/plain",
        as_attachment=True
    )


# & LIST ALL PROMO
@admin.route('/promo')
@admin_authentication_required
@limiter.limit("30 per minute")
def list_promo():
    promo_codes = PromoCode.query.all()
    active_promo_count = PromoCode.query.filter(
        PromoCode.users < PromoCode.limit,
        PromoCode.expiry >= today,
    ).count()

    return jsonify({
        'status': 200,
        'error': None,
        'message': None,
        'details': {
            'total_promo': len(promo_codes),
            'active_promo': active_promo_count,
        },
        'output_obj': [{
            'code': promo.code,
            'sponsor': promo.sponsor,
            'users': promo.users,
            'credits': promo.credits,
            'discount': promo.discount,
            'available_plans': promo.available_plans,
            'limit': promo.limit,
            'expiry': promo.expiry,
        } for promo in promo_codes]
    }), 200


# & CREATE NEW PROMO
@admin.route('/promo/new', methods=['POST'])
@admin_authentication_required
@limiter.limit("30 per minute")
def new_promo():
    # ACCESS JSON DATA
    data = request.json
    code = data.get('code')
    sponsor = data.get('sponsor')
    credits = data.get('credits')
    discount = data.get('discount')
    available_plans = data.get('plans').split(',')
    limit = data.get('limit')
    expiry = data.get('expiry') # YYYY-MM-DD

    # DATA PROCESSING & VALIDATION
    expiry_date = datetime.strptime(expiry, '%Y-%m-%d').date()
    if (not code) or (not limit):
        return jsonify({
            'status': 400,
            'error': 'InvalidDataError',
            'message': 'One or more important cells are missing.',
            'details': {
                'code': code,
                'limit': limit,
            },
        }), 400

    # CREATE PROMO OBJECT
    new_promo = PromoCode(
        code=code,
        sponsor=sponsor,
        credits=credits,
        discount=discount,
        available_plans=available_plans,
        limit=limit,
        expiry=expiry_date,
    )

    # ADD PROMO OBJ TO DB ROW AND SAVE
    db.session.add(new_promo)
    db.session.commit()

    # RETURN RESPONSE
    return jsonify({
        'status': 200,
        'error': None,
        'message': 'New promo code added successfully!',
        'details': {
            'code': code,
            'sponsor': sponsor,
            'credits': credits,
            'discount': discount,
            'available_plans': available_plans,
            'limit': limit,
            'expiry': expiry_date,
        }
    }), 200


# & GET/PATCH/DELETE SPECIFIC PROMO CODE
@admin.route('/promo/<id>', methods=['GET', 'PATCH', 'DELETE'])
@admin_authentication_required
@limiter.limit("30 per minute")
def crud_promo(id: str):
    # VALIDATE DATA
    if (not id) or (not id.isdigit()):
        return jsonify({
            'status': 400,
            'error': 'InvalidDataError',
            'message': f"Id '{id}' is invalid.",
            'details': None,
        }), 400
    
    promo_code = PromoCode.query.get(int(id))
    if (not promo_code):
        return jsonify({
            'status': 404,
            'error': 'PromoNotFoundError',
            'message': f'Promo code [promo-{id}] not found.',
            'details': None,
        }), 404

    if (request.method == 'GET'):
        return jsonify({
            'status': 200,
            'error': None,
            'message': None,
            'details': {
                'code': promo_code.code,
                'sponsor': promo_code.sponsor,
                'users': promo_code.users,
                'credits': promo_code.credits,
                'discount': promo_code.discount,
                'available_plans': promo_code.available_plans,
                'limit': promo_code.limit,
                'expiry': promo_code.expiry,
            },
            'output_obj': promo_code.to_dict()
        }), 200

    elif (request.method == 'PATCH'):
        # ACCESS JSON DATA
        data = request.json
        credits = data.get('credits', promo_code.credits)
        available_plans = data.get('available_plans', promo_code.available_plans)
        limit = data.get('limit', promo_code.limit)
        expiry = data.get('expiry')
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date() if expiry else promo_code.expiry

        # UPDATE PROMO CODE & SAVE DB
        promo_code.credits = credits
        promo_code.available_plans = available_plans
        promo_code.limit = limit
        promo_code.expiry = expiry_date
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            'status': 200,
            'error': None,
            'message': 'Promo Code updated successfully!',
            'details': {
                'credits': promo_code.credits,
                'available_plans': promo_code.available_plans,
                'limit': promo_code.limit,
                'expiry': promo_code.expiry,
            },
        }), 200
    
    else:
        # DELETE PROMO CODE
        db.session.delete(promo_code)
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            'status': 200,
            'error': None,
            'message': 'Promo Code delete successfully!',
            'details': None,
        }), 200


# & INCREASE/DECREASE USER'S CREDITS
@admin.route('/credits/manipulate', methods=['PATCH'])
@admin_authentication_required
@limiter.limit("30 per minute")
def manipulate_credits():
    # ACCESS JSON DATA
    data = request.json
    userid = data.get('userid')
    amount = data.get('credits')
    amount = int(amount) if amount else 0

    # DATA VALIDATION
    if (not userid) or (not amount):
        return jsonify({
            'status': 400,
            'error': 'InvalidDataError',
            'message': 'One or more important fields are missing.',
            'details': {
                'userid': userid,
                'credits': amount,
            },
        }), 400

    user = User.query.get(userid)
    if (not user):
        return jsonify({
            'status': 404,
            'error': 'UserNotFoundError',
            'message': f'User [user-{userid}] not found',
            'details': None,
        }), 404

    # UPDATE CREDITS & SAVE DB
    user.total_credits += amount
    user.left_credits += amount
    db.session.commit()

    # RETURN RESPONSE
    return jsonify({
        'status': 200,
        'error': None,
        'message': 'Credits updated successfully!',
        'details': {
            'added_credits': amount,
            'previous_total': user.total_credits - amount,
            'previous_left': user.left_credits - amount,
            'new_total': user.total_credits,
            'new_left': user.left_credits,
        },
    }), 200


