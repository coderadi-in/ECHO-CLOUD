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
# ORDER SPECIFIC END-POINTS
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
                extract('year', Order.ordered_on), today.year
            ).all()

            for order_info in orders_info:
                product_info = Product.query.get(order_info.product_id)
                price_list.append(product_info.price)

            orders_qty.append(sum(orders_qty))
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
            ).count()

            orders_list.append(orders_info)

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