"""
Data specific api routes management file for the Project.

Manages the routes of Data specific api.
"""

# ==================================================
# SETUP
# ==================================================

# ? IMPORTS
from flask import Blueprint, jsonify, request, send_file
from plugins import *
from models import *
from io import BytesIO

# | ROUTER INIT
data_exporter = Blueprint('data_exporter', __name__, url_prefix='/api/data_exporter')

# | AUXILIARY REFERENCES
today = date.today()

# ==================================================
# END-POINTS
# ==================================================

# & EXPORT REVENUE DATA
@data_exporter.route('/revenue', methods=['POST'])
@limiter.limit("20 per minute")
@login_required
def export_revenue():
    # AUXILIARY DATA VALUES
    last_month = today.replace(day=1) - relativedelta(month=1)
    next_month = today.replace(day=28) + timedelta(days=4)
    this_month = next_month - timedelta(days=next_month.day)
    start_index, end_index = None, None

    # EMPTY DATA
    buffer = BytesIO()
    raw_df = {
        'Title': [],
        'Price': [],
        'Ordered Qty': [],
        'Sales Amt': [],
    }

    # RESOURCES FROM CLIENT-SIDE
    data = request.get_json()
    start_range = data.get('startRange')
    end_range = data.get('endRange')

    # DATA PROCESSING
    start_index = datetime.strptime(start_range, "%Y-%m-%d").date() if start_range else last_month
    end_index = datetime.strptime(end_range, "%Y-%m-%d").date() if end_range else this_month

    # FETCH SALES INFO
    for product in current_user.products:
        orders_count = Order.query.filter(
            Order.user == current_user.id,
            Order.status == 'accepted',
            Order.product_id == product.id,
            Order.ordered_on >= start_index,
            Order.ordered_on <= end_index
        ).all()

        sales_qty = sum([order.quantity for order in orders_count])

        raw_df['Title'].append(product.title)
        raw_df['Price'].append(product.price)
        raw_df['Ordered Qty'].append(len(orders_count))
        raw_df['Sales Amt'].append(orders_count * product.price * sales_qty)

    # INITIALIZE DATA BYTES TO SEND
    df = pd.DataFrame(raw_df)
    df.to_csv(buffer)
    buffer.seek(0)

    # RETURN DATA
    return send_file(
        buffer,
        as_attachment=False,
        download_name='revenue.csv',
        mimetype='text/csv'
    )

# & EXPORT ANALYTICS DATA
@data_exporter.route('/analytics', methods=['POST'])
@limiter.limit("20 per minute")
@login_required
def export_analytics():
    # AUXILIARY DATA VALUES
    last_month = today.replace(day=1) - relativedelta(month=1)
    next_month = today.replace(day=28) + timedelta(days=4)
    this_month = next_month - timedelta(days=next_month.day)
    start_index, end_index = None, None

    # EMPTY DATA
    buffer = BytesIO()
    raw_df = {
        'Date': [],
        'Title': [],
        'Price': [],
        'Ordered Qty': [],
        'Sales Amt': [],
    }

    # RESOURCES FROM CLIENT-SIDE
    data = request.get_json()
    start_range = data.get('startRange')
    end_range = data.get('endRange')

    # DATA PROCESSING
    start_index = datetime.strptime(start_range, "%Y-%m-%d").date() if start_range else last_month
    end_index = datetime.strptime(end_range, "%Y-%m-%d").date() if end_range else this_month

    # FETCH SALES INFO
    orders_list = Order.query.filter(
        Order.user == current_user.id,
        Order.ordered_on >= start_index,
        Order.ordered_on <= end_index
    ).all()

    # POPULATE SALES INFO
    for order in orders_list:
        product = Product.query.get(order.product_id)
        raw_df['Date'].append(order.ordered_on)
        raw_df['Title'].append(product.title)
        raw_df['Price'].append(product.price)
        raw_df['Ordered Qty'].append(order.quantity)
        raw_df['Sales Amt'].append(order.quantity * product.price)

    # SAVE SALES INFO
    df = pd.DataFrame(raw_df)
    df.to_csv(buffer)
    buffer.seek(0)

    # RETURN RESPONSE
    return send_file(
        buffer,
        as_attachment=False,
        download_name="analytics.csv",
        mimetype="text/csv",
    )