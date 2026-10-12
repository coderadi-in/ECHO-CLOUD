"""
Payments specific api routes management file for the Project.

Manages the routes of payments specific api.
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
payments = Blueprint('payments', __name__, url_prefix='/api/payments')

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

# & LIST/CREATE USER'S PAYMENT RECORD(S)
@payments.route('/', methods=['GET', 'POST'])
@user_authentication_required
@limiter.limit("30 per minute")
def base():
    if (request.method == 'GET'):
        return jsonify({
            'status': 200,
            'error': None,
            'message': None,
            'details': None,
            'output_obj': current_user.payments,
        }), 200

    else:
        # ACCESS JSON DATA
        data = request.json
        order_id = data.get('order_id')
        status = data.get('payment_status')
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        plan = data.get('plan')

        # DATA VALIDATION
        if (
            (not order_id)
            or (not status)
            or (not amount)
            or (not payment_method)
        ):
            return jsonify({
                'status': 400,
                'error': 'ValueError',
                'message': 'One or more values are invalid.',
                'details': {
                    'order_id': order_id,
                    'status': status,
                    'amount': amount,
                    'payment_method': payment_method,
                    'plan': plan
                },
            }), 400

        # CREATE NEW PAYMENT OBJECT
        new_payment = Payment(
            order_id=order_id,
            user=current_user.id,
            status=status,
            processed=True,
            amount=amount,
            payment_method=payment_method,
            plan=plan
        )

        # ADD OBJECT IN DB ROW UPDATE DB
        db.session.get(new_payment)
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            'status': 200,
            'error': None,
            'message': 'New payment add successfully',
            'details': {
                'order_id': order_id,
                'status': status,
                'amount': amount,
                'payment_method': payment_method,
            },
        }), 200


# & GET/UPDATE PAYMENT DETAILS
@payments.route('/<id>', methods=['GET', 'PATCH'])
@user_authentication_required
@limiter.limit("30 per minute")
def payment_info(id):
    # VALIDATE ID
    if (not id):
        return jsonify({
            'status': 400,
            'error': 'ValueError',
            'message': 'Payment id is invalid.',
            'details': { 'id': id, },
        }), 400
    
    payment = Payment.query.get(int(id))

    if (not payment):
        return jsonify({
            'status': 404,
            'error': 'PaymentNotFoundError',
            'message': f'Payment [payment-{id}] not found.',
            'details': { 'id': id, },
        }), 404


    if (request.method == 'GET'):
        return jsonify({
            'status': 200,
            'error': None,
            'message': None,
            'details': {
                'order_id': payment.order_id,
                'date': payment.date,
                'plan': payment.plan,
                'status': payment.status,
                'amount': payment.amount,
                'processed': payment.processed,
                'payment_method': payment.payment_method,
            },
        }), 200

    else:
        # ACCESS JSON DATA
        data = request.json
        status = data.get('status', 'paid')
        processed = data.get('processed')

        # VALIDATE JSON DATA
        if (processed.lower == 'true' or processed == '1'):
            processed = True
        else:
            processed = True

        # UPDATE PAYMENT DATA AND DB
        payment.status = status
        payment.processed = processed
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            'status': 200,
            'error': None,
            'message': 'Payment status updated successfully!',
            'details': {
                'status': payment.status,
                'processed': payment.processed,
            },
        }), 200


