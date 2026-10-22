"""
Application user specific api routes management file for the Project.

Manages the routes of user specific api.
"""

# ==================================================
# SETUP
# ==================================================

# ? IMPORTS
from flask import Blueprint, jsonify, request
from plugins import *
from models import *
from functools import wraps
from collections import defaultdict

# ! ROUTER INIT
user = Blueprint('user', __name__, url_prefix='/api/user')

# * AUXILIARY FUNCTION TO CHECK IF CURRENT USER IS AUTHENTICATED
def user_authentication_required(func: callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if (not current_user) or (not current_user.is_authenticated):
            return jsonify({
                "status": 401,
                "error": "LoginRequiredError",
                "message": "User is not logged in.",
                "details": None,
            }), 401

        return func(*args, **kwargs)
    return wrapper


# ==================================================
# ENDPOINTS
# ==================================================

# & GET TOTAL/LEFT CREDITS AND PLAN DETAILS
@user.route('/credits')
@user_authentication_required
@limiter.limit("30 per minute")
def credits():    
    return jsonify({
        "status": 200,
        "error": None,
        "message": None,
        "details": {
            "total_credits": current_user.total_credits,
            "left_credits": current_user.left_credits,
            "last_plan": current_user.last_plan,
            "current_plan": current_user.current_plan,
            "renewal_date": current_user.renewal_date,
            "plan_info": ACCOUNT_PLANS.get(current_user.current_plan.lower()),
        }
    }), 200


# & GET CURRENT MONTH'S CREDITS USAGE REPORT
@user.route('/credits/usage')
@user_authentication_required
@limiter.limit("30 per minute")
def get_monthly_usage():
    # VALUES DEFINITION
    today = date.today()
    start = today.replace(day=1)

    dates, counts = [], []
    current = start
    gens = defaultdict(int)

    # FETCH CURRENT USER'S GENERATIONS
    captions = Caption.query.filter(
        Caption.user == current_user.id,
        extract('month', Caption.created_at) == today.month
    ).all()
    
    headlines = Headline.query.filter(
        Headline.user == current_user.id,
        extract('month', Headline.created_at) == today.month
    ).all()

    barcode_sheets = BarcodeSheet.query.filter(
        BarcodeSheet.user == current_user.id,
        extract('month', BarcodeSheet.created_at) == today.month,
    ).all()

    # COUNT GENERATIONS IN DICT [DEFAULT = 0]
    for caption in captions:
        gens[caption.created_at] += 1

    for headline in headlines:
        gens[headline.created_at] += 1

    for barcode in barcode_sheets:
        gens[barcode.created_at] += 1

    # APPEND ALL COUNTS AND DATES IN A LIST
    while (current <= today):
        dates.append(current.strftime("%d"))
        counts.append(gens[current])

        current += timedelta(days=1)

    # RETURN RESPONSE
    return jsonify({
        "dates": dates,
        "counts": counts
    })


# & LIST CURRENT USER'S PAYMENTS
@user.route('/payments')
@user_authentication_required
@limiter.limit("30 per minute")
def payments():
    return jsonify({
        "status": 200,
        "error": None,
        "message": None,
        "details": { "payments": current_user.payments, },
    }), 200


# & LIST CURRENT USER'S ORDERS
@user.route('/orders')
@user_authentication_required
@limiter.limit("30 per minute")
def orders():
    return jsonify({
        "status": 200,
        "error": None,
        "message": None,
        "details": { "orders": current_user.orders, },
    }), 200


# & LIST CURRENT USER'S PRODUCTS
@user.route('/products')
@user_authentication_required
@limiter.limit("30 per minute")
def products():
    return jsonify({
        "status": 200,
        "error": None,
        "message": None,
        "details": { "products": current_user.products, },
    }), 200


# & LIST CURRENT USER'S CAPTIONS
@user.route('/captions')
@user_authentication_required
@limiter.limit("30 per minute")
def captions():
    return jsonify({
        "status": 200,
        "error": None,
        "message": None,
        "details": { "captions": current_user.captions, },
    }), 200


# & LIST CURRENT USER'S HEADLINES
@user.route('/headlines')
@user_authentication_required
@limiter.limit("30 per minute")
def headlines():
    return jsonify({
        "status": 200,
        "error": None,
        "message": None,
        "details": { "headlines": current_user.headlines, },
    }), 200


# & LIST CURRENT USER'S BARCODE SHEETS
@user.route('/barcode-sheets')
@user_authentication_required
@limiter.limit("30 per minute")
def barcode_sheets():
    return jsonify({
        "status": 200,
        "error": None,
        "message": None,
        "details": { "barcode-sheets": current_user.barcode_sheets, },
    }), 200


# & LIST CURRENT USER'S SAVED GENERATIONS
@user.route('/saved')
@user_authentication_required
@limiter.limit("30 per minute")
def saved():
    return jsonify({
        "status": 200,
        "error": None,
        "message": None,
        "details": { "saved": current_user.saved, },
    }), 200


# & GET CURRENT USER'S UNLOCKED FEATURES
@user.route('/features')
@user_authentication_required
@limiter.limit("30 per minute")
def unlocked_features():
    # FETCH INFORMATION
    plan_info = ACCOUNT_PLANS.get(current_user.current_plan)
    features = plan_info['unlocked_features']

    # RETURN RESPONSE
    return jsonify({
        'status': 200,
        'error': None,
        'message': None,
        'output_obj': features,
    })