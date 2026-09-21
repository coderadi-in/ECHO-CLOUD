"""
Product orders specific api routes management file for the Project.

Manages the routes of Product orders specific api.
"""

# ==================================================
# SETUP
# ==================================================

# ? IMPORTS
from flask import Blueprint, jsonify, request, send_file
from plugins import *
from models import *

# | ROUTER INIT
orders = Blueprint('orders', __name__, url_prefix='/api/orders')

# | AUXILIARY REFERENCES
today = date.today()

# ==================================================
# FETCH ORDER SPECIFIC END-POINTS
# ==================================================

# & FETCH QUANTITY OF ORDERS SOLD IN A YEAR
@orders.route('/fetch/qty-value/by-year')
@limiter.limit("20 per minute")
@login_required
def fetch_orders_by_year():
    # EMPTY DATA-VALUES
    orders_qty = []
    order_amounts = []

    # FETCH ORDERS
    try:
        for month in range(1, 13):
            price_list = []

            orders_info = Order.query.filter(
                Order.user == current_user.id,
                extract('month', Order.ordered_on) == month,
                extract('year', Order.ordered_on) == today.year,
                Order.status == 'accepted'
            ).all()

            month_qty = sum([order.quantity for order in orders_info])

            for order_info in orders_info:
                product_info = Product.query.get(order_info.product_id)
                price_list.append(product_info.price * month_qty)

            orders_qty.append(month_qty)
            order_amounts.append(sum(price_list))
            

    except:
        return jsonify({
            'status': 500,
            'output': 'Something went wrong while processing your request!'
        }), 500

    # RETURN OUTPUT
    return jsonify({
        'status': 200,
        'output': {
            'qty': orders_qty,
            'amt': order_amounts
        }
    }), 200

# & FETCH QUANTITY OF EACH PRODUCT SOLD IN A MONTH
@orders.route('/fetch/prod-qty/by-month')
@limiter.limit("20 per minute")
@login_required
def fetch_prod_qty_by_month():
    # EMPTY DATA-VALUES
    product_list = []
    orders_list = []

    # FETCH ORDERS
    try:
        for product in current_user.products:
            product_list.append(product.title)

            orders_info = Order.query.filter(
                Order.user == current_user.id,
                Order.product_id == product.id,
                extract('month', Order.ordered_on) == today.month,
                Order.status == 'accepted'
            ).all()

            order_qty = sum([order.quantity for order in orders_info])

            orders_list.append(order_qty)

    except:
        return jsonify({
            'status': 500,
            'output': 'Something went wrong while processing your request!'
        }), 500

    # RETURN OUTPUT
    return jsonify({
        'status': 200,
        'output': {
            'products': product_list,
            'qty': orders_list
        }
    }), 200

# & FETCH ORDERS BY DATE RANGE
@orders.route('/fetch/prod-qty/by-range', methods=['POST'])
@limiter.limit("20 per minute")
@login_required
def fetch_orders_by_date_range():
    # ACCESS REQUEST VALUES
    req_values = request.get_json()
    start_date = datetime.strptime(req_values.get('start'), "%Y-%m-%d").date()
    end_date = datetime.strptime(req_values.get('end'), "%Y-%m-%d").date()

    # VALIDATE VALUES
    if (not start_date) or (not end_date):
        return jsonify({
            'status': 400,
            'message': "Can't fetch date range."
        }), 400

    # FETCH ORDERS
    orders_list = Order.query.filter(
        Order.user == current_user.id,
        Order.ordered_on >= start_date,
        Order.ordered_on <= end_date
    ).all()

    orders_json = [{
        'id': order.id,
        'ordered_on': order.ordered_on.strftime('%d|%m|%Y'),
        'product': Product.query.get(order.product_id).title,
        'amount': Product.query.get(order.product_id).price,
        'qty': order.quantity,
        'status': order.status
    } for order in orders_list]

    # RETURN RESPONSE
    return jsonify({
        'status': 200,
        'output': orders_json
    }), 200

# ==================================================
# PUSH ORDER SPECIFIC END-POINTS
# ==================================================

# & CREATE NEW ORDER
@orders.route('/push', methods=['POST'])
@limiter.limit("100 per minute")
def push_order():
    # SOURCE VALIDATION
    source_url = request.origin
    user = User.query.filter(
        User.site_url.contains(source_url)
    ).first()

    if (not user):
        return jsonify({
            'status': 403,
            'message': 'The source looks suspicious'
        }), 403

    # ACCESS SOURCE DATA
    source_id = request.form.get('product_id')
    quantity = request.form.get('product_qty')
    quantity = int(quantity) if quantity.isdigit() else 1

    # VALIDATE SOURCE DATA
    if (not Product.query.get(source_id)):
        return jsonify({
            'status': 422,
            'message': "The source id isn't compatible."
        }), 422

    # CREATE NEW ORDER
    new_order = Order(
        user=user.id,
        product_id=source_id,
        quantity=quantity
    )

    # SAVE NEW ORDER TO DB
    db.session.add(new_order)
    db.session.commit()

    return jsonify({
        'status': 200,
        'message': "The order has been accepted."
    }), 200