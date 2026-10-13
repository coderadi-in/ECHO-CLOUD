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
from functools import wraps

# | ROUTER INIT
orders = Blueprint('orders', __name__, url_prefix='/api/orders')

# | AUXILIARY REFERENCES
today = date.today()

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

# & LIST/ADD CURRENT USER'S ORDERS, WITH FILTERS
@orders.route('/', methods=['GET', 'POST'])
@limiter.limit("30 per minute")
def base():
    if request.method == 'GET':
        # ACCESS URL DATA (FILTERS)
        order_status = request.args.get('order_status')
        product_id = request.args.get('product_id')
        view = request.args.get('view')      # 'by-year' | 'by-product' | 'by-range'
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        start = request.args.get('start')     # 'YYYY-MM-DD'
        end = request.args.get('end')       # 'YYYY-MM-DD'

        try:
            # -----------------------------------------------------------
            # BASE QUERY (common filters applied to all views)
            # -----------------------------------------------------------
            query = Order.query.filter(Order.user == current_user.id)

            if (order_status):
                query = query.filter(Order.status == order_status)

            if (product_id):
                query = query.filter(Order.product_id == product_id)

            # -----------------------------------------------------------
            # VIEW 1: QUANTITY + AMOUNT SOLD PER MONTH IN A YEAR
            # ?view=by-year&year=2025
            # -----------------------------------------------------------
            if (view == 'by-year'):
                orders_qty    = []
                order_amounts = []
                target_year   = year or today.year

                for month in range(1, 13):
                    month_orders = query.filter(
                        extract('month', Order.ordered_on) == month,
                        extract('year',  Order.ordered_on) == target_year
                    ).all()

                    orders_qty.append(sum(order.quantity for order in month_orders))
                    order_amounts.append(sum(
                        Product.query.get(order.product_id).price * order.quantity
                        for order in month_orders
                    ))

                return jsonify({
                    'status': 200,
                    'error': None,
                    'message': None,
                    'details': {
                        'qty': orders_qty,
                        'amt': order_amounts,
                    },
                }), 200

            # -----------------------------------------------------------
            # VIEW 2: QUANTITY OF EACH PRODUCT SOLD IN A MONTH
            # ?view=by-product&year=2025&month=6
            # -----------------------------------------------------------
            if (view == 'by-product'):
                product_list = []
                orders_list  = []
                target_month = month or today.month
                target_year = year or today.year

                products = current_user.products
                if (product_id):
                    products = [prod for prod in products if str(prod.id) == str(product_id)]

                for product in products:
                    product_list.append(product.title)

                    product_orders = query.filter(
                        Order.product_id == product.id,
                        extract('month', Order.ordered_on) == target_month,
                        extract('year',  Order.ordered_on) == target_year
                    ).all()

                    orders_list.append(sum(order.quantity for order in product_orders))

                return jsonify({
                    'status': 200,
                    'error': None,
                    'message': None,
                    'details': {
                        'products': product_list,
                        'qty': orders_list
                    },
                }), 200

            # -----------------------------------------------------------
            # VIEW 3: ORDERS BY DATE RANGE
            # ?view=by-range&start=2025-01-01&end=2025-06-30
            # -----------------------------------------------------------
            if (view == 'by-range'):
                if (not start) or (not end):
                    return jsonify({
                        'status': 400,
                        'error': "ValueError",
                        'message': "Can't fetch date range.",
                        'details': {
                            'start': start,
                            'end': end,
                        },
                    }), 400

                start_date = datetime.strptime(start, "%Y-%m-%d").date()
                end_date = datetime.strptime(end, "%Y-%m-%d").date()

                orders_list = query.filter(
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

                return jsonify({
                    'status': 200,
                    'error': None,
                    'message': None,
                    'details': None,
                    'output_obj': orders_json
                }), 200

            # -----------------------------------------------------------
            # DEFAULT: ALL FILTERED ORDERS (no view specified)
            # -----------------------------------------------------------
            orders_list = query.all()
            orders_json = [{
                'id': order.id,
                'ordered_on': order.ordered_on.strftime('%d|%m|%Y'),
                'product': Product.query.get(order.product_id).title,
                'amount': Product.query.get(order.product_id).price,
                'qty': order.quantity,
                'status': order.status
            } for order in orders_list]

            return jsonify({
                'status': 200,
                'error': None,
                'message': None,
                'details': None,
                'output_obj': orders_json
            }), 200

        except Exception as e:
            return jsonify({
                'status': 500,
                'error': 'InternalServerError',
                'message': e,
                'details': None,
            }), 500

    else:
        # ACCESS SOURCE AND VALIDATE
        source_url = request.origin
        user = User.query.filter(
            User.site_url.contains(source_url)
        ).first()

        if (not user):
            return jsonify({
                "status": 403,
                'error': 'InvalidSourceError',
                'message': 'The request came from invalid source.',
                'details': None
            }), 403

        # ACCESS SOURCE DATA
        product_id = request.form.get('product_id')
        quantity = request.form.get('product_qty', 1, type=int)

        # SOURCE DATA VALIDATION
        if (not Product.query.get(product_id)):
            return jsonify({
                'status': 422,
                'error': 'IncompatibleDataError',
                'message': "The source id is not compatible.",
                'details': None
            }), 422

        # CREATE NEW ORDER OBJECT
        new_order = Order(
            user=user.id,
            product_id=product_id,
            quantity=quantity,
        )

        # ADD ORDER TO DB ROW
        db.session.add(new_order)
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            'status': 200,
            'error': None,
            'message': 'Order added successfully!',
            'details': {
                'order_id': new_order.id,
                'product_id': product_id,
                'quantity': quantity,
                'ordered_on': new_order.ordered_on,
            },
        }), 200


# & GET/DELETE ORDER DETAILS
@orders.route('/<id>', methods=['GET', 'DELETE'])
@user_authentication_required
@limiter.limit("30 per minute")
def order(id):
    # FILTER & VALIDATE ORDER
    if (not id):
        return jsonify({
            'status': 400,
            'error': 'ValueError',
            'message': 'Order id is invalid.',
            'details': { 'id': id, },
        }), 400
    
    order = Order.query.get(int(id))

    if (not order):
        return jsonify({
            'status': 404,
            'error': 'OrderNotFoundError',
            'message': f'Order [order-{id}] not found.',
            'details': { 'id': id, },
        }), 404

    if (request.method == 'GET'):
        # FETCH PRODUCT INFO
        product_info = Product.query.get(order.product_id)

        return jsonify({
            'status': 200,
            'product_id': order.product_id,
            'product_title': product_info.title,
            'product_price': product_info.price,
            'quantity': order.quantity,
            'amount': product_info.price * order.quantity,
            'ordered_on': order.ordered_on,
            'status': order.status
        }), 200

    if (request.method == 'DELETE'):
        # MARK ORDER AS DELETED
        order.deleted = True
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            'status': 200,
            'error': None,
            'message': 'Product marked as deleted.',
            'details': {
                'product_id': order.product_id,
                'order_id': order.id,
            },
        }), 200


# & UPDATE ORDER STATUS
@orders.route('/<id>/status', methods=['PATCH'])
@user_authentication_required
@limiter.limit("30 per minute")
def update_status(id):
    # FILTER & VALIDATE ORDER
    if (not id):
        return jsonify({
            'status': 400,
            'error': 'ValueError',
            'message': 'Order id is invalid.',
            'details': { 'id': id, },
        }), 400
    
    order = Order.query.get(int(id))

    if (not order):
        return jsonify({
            'status': 404,
            'error': 'OrderNotFoundError',
            'message': f'Order [order-{id}] not found.',
            'details': { 'id': id, },
        }), 404

    # ACCESS JSON DATA AND VALIDATE
    data = request.json
    status = data.get('status')
    
    if (not status) or (status not in ['accepted', 'rejected', 'unrecognized']):
        return jsonify({
            'status': 400,
            'error': 'IncompatibleStatusError',
            'message': f'The status {status} is invalid.',
            'details': { 'accepted_values': ['accepted', 'rejected', 'unrecognized'], },
        }), 400

    # UPDATE ORDER STATUS AND UPDATE DB
    order.status = status
    db.session.commit()

    # RETURN RESPONSE
    return jsonify({
        'status': 200,
        'error': None,
        'message': 'Order status updated successfully!',
        'details': None
    }), 200


