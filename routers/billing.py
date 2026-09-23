"""
Application billing routes management file for the Project.

Manages the routes of billing.
"""

# ==================================================
# SETUP
# ==================================================

# ? IMPORTS
from flask import Blueprint, render_template, jsonify, redirect, url_for, send_file, request
from uuid import uuid4
from io import BytesIO
from plugins import *
from models import *

# ! INITS
billing = Blueprint('billing', __name__, url_prefix='/billing')

# ==================================================
# ROUTES
# ==================================================

# & BILLING PAGE ROUTE
@billing.route('/')
@login_required
@limiter.limit("30 per minute")
def plans():
    return render_template('pages/billing.html')

# & UPGRADE ROUTE
@billing.route("/create-order", methods=["POST"])
@login_required
@limiter.limit("5 per minute")
def create_order():
    # ACCESS REQUEST VALUES
    request_data = request.get_json()
    plan_name = request_data.get('planName')

    if (not plan_name):
        return jsonify({ "success": False, }), 400

    response = initiate_payment_order(plan_name)

    # Fetch response status
    if (response["status"] != 200):
        return jsonify({ "success": False, }), 500

    order = response["order"]

    # Return order details
    return jsonify({
        "success": True,
        "key": os.getenv("RZP_ID_TEST"),
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
    })
    
# & PAYMENTS ROUTE
@billing.route('/payments')
@login_required
@limiter.limit("5 per minute")
def check_payment_status():
    # Fetch URL args
    order_id = request.args.get("order_id")
    payment_id = request.args.get("payment_id")
    signature = request.args.get("signature")

    if (Payment.query.filter_by(order_id=order_id).first()):
        flash("The payment was already processed.", "check")
        return redirect(url_for('app.dashboard'))
    
    # Signature verification
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })

    except Exception:
        flash("Payment verification failed.", "error")
        return redirect(url_for("billing.billing"))
    
    # Fetch status
    response = fetch_payment_status(payment_id)
    info = response['payment']
    payment_status = info['status']
    amount = info['amount']
    payment_method = info['method']
    currency = info['currency']

    # Add to DB
    payment = Payment(
        order_id=order_id,
        user=current_user.id, 
        status=payment_status,
        processed=True,
        amount=amount,
        payment_method=payment_method
    )

    db.session.add(payment)
    db.session.commit()

    # Return response
    if (payment_status == "captured"):
        upgrade_plan()

        return render_template(f"events/paid.html", data={
            "order_id": order_id,
            "plan": "Pro",
            "status": payment_status,
            "amount": amount,
            "currency": currency,
            "id": payment.id,
            "date": payment.date,
            "method": payment_method,
            "credits": ACCOUNT_PLANS["pro"],
        })
    
    else:
        flash("We can't process your payment.", "error")
        flash("If the amount is deducted, it'll be refunded within 2 business days.", "check")
        return redirect(url_for('app.dashboard'))
    
# & EXPORT HISTORY ROUTE
@billing.route('/history/export')
@login_required
@limiter.limit("30 per minute")
def export_history():
    payments_history = current_user.payments
    buffer = BytesIO()

    payments_df = pd.DataFrame({
        'date': payment.date,
        'order_id': payment.order_id,
        'plan': payment.plan,
        'amount': payment.amount,
        'status': payment.status,
        'processed': payment.processed
    } for payment in payments_history)
    payments_df.to_csv(buffer)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name='payments.csv',
        mimetype='text/csv'
    )

# & PROMO CODE ROUTE
@billing.route('/promo-code', methods=['POST'])
@login_required
@limiter.limit("10 per hour")
def apply_promo_code():
    # ACCESS FORM DATA
    promo_code = request.form.get('promo')

    # FORM VALIDATION
    if (not promo_code):
        flash("Probably you haven't entered any promo code.", "error")
        return redirect(url_for('billing.plans'))

    # PROMO CODE FETCHING
    promo_codes = PromoCode.query.filter(
        PromoCode.expiry >= date.today(),
        PromoCode.users < PromoCode.limit,
    ).all()

    # MATCHING PROMO CODE
    for code in promo_codes:
        if (
            promo_code == code.code and
            current_user not in code.users_list
        ):
            current_user.total_credits += code.credits
            current_user.left_credits += code.credits
            code.users += 1
            code.users_list.append(current_user)
            
            db.session.commit()
            flash("Promo code applied to your credit balance.", "redeem")
            return redirect(url_for('app.dashboard'))
        
    # RETURN RESPONSE
    flash("The promo code you entered is either wrong or been expired!", "error")
    return redirect(url_for('billing.plans'))