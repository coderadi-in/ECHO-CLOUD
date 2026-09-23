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
from io import BytesIO
from functools import wraps

# ! ROUTER INIT
admin = Blueprint('admin', __name__, url_prefix='/api/admin')

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
# LOGS API ENDPOINTS
# ==================================================

# & DOWNLOAD
@admin.route('/logs/download')
@admin_authentication_required
def download_logs():
    log_type = request.args.get('log_type')

    file_path = os.path.join(
        current_app.root_path,
        "logs",
        f"{log_type}.log"
    )

    if (not os.path.exists(file_path)):
        return jsonify({
            "status": 404,
            "message": "The file doesn't exists in the application directory"
        }), 404
    
    return send_file(
        file_path,
        download_name=f"{log_type}.log",
        mimetype="text/plain",
        as_attachment=True
    )

# ==================================================
# PROMO API ENDPOINTS
# ==================================================

# & ALL PROMO
@admin.route('/promo/all')
@admin_authentication_required
def all_promo():
    promo_df = pd.read_sql_table('promo_code', db.engine)
    return promo_df.to_dict(), 200

# & NEW PROMO
@admin.route('/promo/new', methods=['POST'])
@admin_authentication_required
def create_promo():
    # ACCESS FORM DATA
    code = request.json.get('code')
    sponsor = request.json.get('sponsor')
    credits = request.json.get('credits')
    discount = request.json.get('discount')
    available_plans = request.json.get('available_plans')
    limit = request.json.get('limit')
    expiry = request.json.get('expiry')

    # DATA VALIDATION
    if (credits and discount):
        discount = None

    # TYPECASTING & SPLITTING
    credits = int(credits) if credits else None
    discount = float(discount) if discount else None
    limit = int(limit) if limit else None
    
    if expiry:
        exp_d, exp_m, exp_y = expiry.split("/")
        expiry = date(int(exp_y), int(exp_m), int(exp_d))
    else:
        expiry = None

    # CREATE NEW PROMO
    new_promo = PromoCode(
        code=code,
        sponsor=sponsor,
        credits=credits,
        discount=discount,
        available_plans=available_plans,
        limit=limit,
        expiry=expiry,
    )

    db.session.add(new_promo)
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "New promo created successfully",
        "output": {
            "id": new_promo.id,
            "code": code,
            "sponsor": sponsor,
            "credits": credits,
            "discount": discount,
            "available_plans": available_plans,
            "limit": limit,
            "expiry": expiry,
        }
    }), 200

# & DELETE PROMO
@admin.route('/promo/delete')
@admin_authentication_required
def delete_promo():
    # ACCESS URL DATA
    promo_id = request.args.get('promo-id')

    # PARAM VALIDATION
    if (not promo_id):
        return jsonify({
            "status": 422,
            "message": "Promo ID is invalid"
        }), 422
    
    # DATABASE FILTER
    promo = PromoCode.query.filter_by(id=int(promo_id)).first()

    # ROW VALIDATION
    if (not promo):
        return jsonify({
            "status": 400,
            "message": "Promo ID does not exist"
        }), 400
    
    # DELETE PROMO
    db.session.delete(promo)
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Promo deleted successfully"
    }), 200

# ==================================================
# CREDITS API ENDPOINTS
# ==================================================

# & INCREASE USER CREDITS
@admin.route('/credits/increase', methods=['POST'])
@admin_authentication_required
def increase_credits():
    # ACCESS JSON DATA AND USER ROW
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    # USER VALIDATION
    if (not user):
        return jsonify({
            "status": 404,
            "message": "User not found!"
        }), 404

    # INCREASE CREDITS
    user.total_credits += int(data['credits'])
    user.left_credits += int(data['credits'])
    db.session.commit()

    # RETURN RESPONSE
    return jsonify({
        "status": 200,
        "message": "Credits increase successfully!",
        "details": {
            "user_email": user.email,
            "increase_credits": data['credits'],
            "total_credits": user.total_credits
        }
    }), 200