"""
Matrices specific api routes management file for the Project.

Manages the routes of Matrices specific api.
"""

# ==================================================
# SETUP
# ==================================================

# ? IMPORTS
from flask import Blueprint, jsonify, request
from plugins import *
from models import *

# | ROUTER INIT
matrices = Blueprint('matrices', __name__, url_prefix='/api/matrices')

# | AUXILIARY REFERENCES
today = date.today()

# ==================================================
# ORDER QUANTITY SPECIFIC
# ==================================================

# & COMPARE WITH PREVIOUS MATRICES BY TIME PERIOD
@matrices.route('/compare/qty/by-time', methods=['POST'])
@limiter.limit("20 per minute")
@login_required
def compare_qty_by_time():
    # ACCESS JSON DATA
    data = request.get_json()
    time_period = data.get('timePeriod')

    try:
        if (time_period == 'month'):
            last_month = today - relativedelta(month=1)

            current_orders_count = Order.query.filter(
                Order.user==current_user.id,
                Order.status=='accepted',
                extract('month', Order.ordered_on) == today.month,
            ).all()

            last_orders_count = Order.query.filter(
                Order.user==current_user.id,
                Order.status=='accepted',
                extract('month', Order.ordered_on) == last_month.month,
            ).all()

            current_orders_qty = sum([order.quantity for order in current_orders_count])
            last_orders_qty = sum([order.quantity for order in last_orders_count])

            delta_orders = current_orders_qty - last_orders_qty
            delta_percentage = delta_orders / last_orders_qty * 100

            return jsonify({
                'status': 200,
                'output': delta_percentage
            }), 200

        elif (time_period == 'year'):
            last_month = today - relativedelta(year=1)

            current_orders_count = Order.query.filter(
                Order.user==current_user.id,
                Order.status=='accepted',
                extract('year', Order.ordered_on) == today.year,
            ).all()

            last_orders_count = Order.query.filter(
                Order.user==current_user.id,
                Order.status=='accepted',
                extract('year', Order.ordered_on) == last_month.year,
            ).all()

            current_orders_qty = sum([order.quantity for order in current_orders_count])
            last_orders_qty = sum([order.quantity for order in last_orders_count])

            delta_orders = current_orders_qty - last_orders_qty
            delta_percentage = delta_orders / last_orders_qty * 100

            return jsonify({
                'status': 200,
                'output': delta_percentage
            }), 200

        else:
            return jsonify({
                'status': 400,
                'output': 0
            }), 400

    except ZeroDivisionError:
        return jsonify({
            'status': 200,
            'output': 100
        }), 200

# & COMPARE WITH PREVIOUS MATRICES BY ORDER STATUS
@matrices.route('/compare/qty/by-status', methods=['POST'])
@limiter.limit("20 per minute")
@login_required
def compare_qty_by_status():
    # ACCESS JSON DATA
    data = request.get_json()
    order_status = data.get('orderStatus', 'accepted')

    try:
        if (order_status not in ['accepted', 'rejected', 'unrecognized']):
            return jsonify({
                'status': 400,
                'output': 0
            }), 400

        last_month = today - relativedelta(month=1)
        
        current_orders_count = Order.query.filter(
            Order.user==current_user.id,
            Order.status==order_status,
            extract('month', Order.ordered_on) == today.month,
        ).all()

        last_orders_count = Order.query.filter(
            Order.user==current_user.id,
            Order.status==order_status,
            extract('month', Order.ordered_on) == last_month.month,
        ).all()

        current_orders_qty = sum([order.quantity for order in current_orders_count])
        last_orders_qty = sum([order.quantity for order in last_orders_count])

        delta_orders = current_orders_qty - last_orders_qty
        delta_percentage = delta_orders / last_orders_qty * 100

        return jsonify({
            'status': 200,
            'output': delta_percentage
        }), 200
        
    except ZeroDivisionError:
        return jsonify({
            'status': 200,
            'output': 0
        }), 200

# & COMPARE PREVIOUS AMOUNT BY TIME PERIOD
@matrices.route('/compare/amt/by-time', methods=['POST'])
@limiter.limit("20 per minute")
@login_required
def compare_amt_by_time():
    # ACCESS JSON DATA
    data = request.get_json()
    time_period = data.get('timePeriod')

    try:
        if (time_period == 'month'):
            last_month = today - relativedelta(month=1)

            current_orders_count = Order.query.filter(
                Order.user==current_user.id,
                Order.status=='accepted',
                extract('month', Order.ordered_on) == today.month,
            ).all()

            last_orders_count = Order.query.filter(
                Order.user==current_user.id,
                Order.status=='accepted',
                extract('month', Order.ordered_on) == last_month.month,
            ).all()

            current_order_amt = sum([Product.query.get(order.product_id).price * order.quantity for order in current_orders_count])
            last_order_amt = sum([Product.query.get(order.product_id).price * order.quantity for order in last_orders_count])

            delta_orders = current_order_amt - last_order_amt
            delta_percentage = delta_orders / last_order_amt * 100

            return jsonify({
                'status': 200,
                'output': delta_percentage
            }), 200

        elif (time_period == 'year'):
            last_year = today - relativedelta(year=1)
            
            current_orders_count = Order.query.filter(
                Order.user==current_user.id,
                Order.status=='accepted',
                extract('month', Order.ordered_on) == today.year,
            ).all()

            last_orders_count = Order.query.filter(
                Order.user==current_user.id,
                Order.status=='accepted',
                extract('month', Order.ordered_on) == last_year.year,
            ).all()

            current_order_amt = sum([Product.query.get(order.product_id).price for order in current_orders_count])
            last_order_amt = sum([Product.query.get(order.product_id).price for order in last_orders_count])

            delta_orders = current_order_amt - last_order_amt
            delta_percentage = delta_orders / last_order_amt * 100

            return jsonify({
                'status': 200,
                'output': delta_percentage
            }), 200

        else:
            return jsonify({
                'status': 400,
                'output': 0
            }), 400

    except ZeroDivisionError:
        return jsonify({
            'status': 200,
            'output': 100
        }), 200

# & COMPARE PREVIOUS AMOUNT BY ORDER STATUS
@matrices.route('/compare/amt/by-status', methods=['POST'])
@limiter.limit("20 per minute")
@login_required
def compare_amt_by_status():
    # ACCESS JSON DATA
    data = request.get_json()
    order_status = data.get('orderStatus', 'accepted')

    try:
        if (order_status not in ['accepted', 'rejected', 'unrecognized']):
            return jsonify({
                'status': 400,
                'output': 0
            }), 400

        last_month = today - relativedelta(month=1)

        current_orders_count = Order.query.filter(
            Order.user==current_user.id,
            Order.status==order_status,
            extract('month', Order.ordered_on) == today.month,
        ).all()

        last_orders_count = Order.query.filter(
            Order.user==current_user.id,
            Order.status==order_status,
            extract('month', Order.ordered_on) == last_month.month,
        ).all()

        current_order_amt = sum([Product.query.get(order.product_id).price * order.quantity for order in current_orders_count])
        last_order_amt = sum([Product.query.get(order.product_id).price * order.quantity for order in last_orders_count])

        delta_orders = current_order_amt - last_order_amt
        delta_percentage = delta_orders / last_order_amt * 100

        return jsonify({
            'status': 200,
            'output': delta_percentage
        }), 200

    except ZeroDivisionError:
        return jsonify({
            'status': 200,
            'output': 0
        }), 200

# & COMPARE SALES QUANTITY OF SPECIFIC PRODUCT
@matrices.route('/compare/product', methods=['POST'])
@limiter.limit("20 per minute")
@login_required
def compare_product_qty():
    # AUXILIARY VALUES
    last_month = today - relativedelta(month=1)
    data = request.get_json()
    product_id = data.get('productId')

    # VALIDATION
    if (not product_id):
        return jsonify({
            'status': 400,
            'message': "Missing values",
            'output': 0
        }), 400

    
    try:
        # FETCH PRODUCT SALES
        current_month_sales = Order.query.filter(
            Order.user == current_user.id,
            Order.product_id == product_id,
            extract('month', Order.ordered_on) == today.month,
            Order.status == 'accepted',
        ).all()
    
        last_month_sales = Order.query.filter(
            Order.user == current_user.id,
            Order.product_id == product_id,
            extract('month', Order.ordered_on) == last_month.month,
            Order.status == 'accepted',
        ).all()

        current_month_qty = sum([order.quantity for order in current_month_sales])
        last_month_qty = sum([order.quantity for order in last_month_sales])
    
        # CALCULATE DELTA
        delta_numerical = current_month_qty - last_month_qty
        delta_percentage = delta_numerical / last_month_qty * 100
    
        return jsonify({
            'status': 200,
            'message': None,
            'output': delta_percentage
        })

    except ZeroDivisionError:
        return jsonify({
            'status': 200,
            'message': None,
            'output': 100
        })

    except:
        return jsonify({
            'status': 500,
            'message': "Can't calculate values",
            'output': 0
        })