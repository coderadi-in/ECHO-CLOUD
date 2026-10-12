"""
Product specific api routes management file for the Project.

Manages the routes of Product specific api.
"""

# ==================================================
# SETUP
# ==================================================

# ? IMPORTS
from flask import Blueprint, jsonify, request
from plugins import *
from models import *
from functools import wraps

# ! ROUTER INIT
products = Blueprint('products', __name__, url_prefix='/api/products')

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

# & LIST/ADD CURRENT USER'S PRODUCTS
@products.route('/', methods=['GET', 'POST'])
@user_authentication_required
@limiter.limit("30 per minute")
def base():
    if (request.method == 'GET'):
        return jsonify({
            "status": 200,
            "error": None,
            "message": None,
            "details": { "products": current_user.products, },
        }), 200

    elif (request.method == 'POST'):
        # ACCESS JSON DATA
        data = request.json
        title = data.get('title')
        price = data.get('price')
        desc = data.get('desc') or data.get('description')

        # CREATE PRODUCT OBJECT
        new_prod = Product(
            user=current_user.id,
            title=title,
            price=price,
            desc=desc,
        )

        # ADD PRODUCT TO DB ROW
        db.session.add(new_prod)
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            "status": 200,
            "error": None,
            "message": "Product added successfully!",
            "details": {
                "id": new_prod.id,
                "title": title,
                "price": price,
                "description": desc,
            }
        }), 200


# & GET/UPDATE/DELETE PRODUCT DETAILS
@products.route('/<id>', methods=['GET', 'PATCH', 'DELETE'])
@user_authentication_required
@limiter.limit("30 per minute")
def details(id):
    # ----- AUXILIARY BODY -----
    # DATA VALIDATION
    if (not id):
        return jsonify({
            "status": 400,
            "error": "ValueError",
            "message": f"id [{id}] is invalid.",
            "details": None,
        }), 400

    product = Product.query.get(int(id))

    if (not product):
        return jsonify({
            "status": 404,
            "error": "ProductNotFoundError",
            "message": f"Product [prod-{id}] not found.",
            "details": None,
        }), 404

    # ----- MAIN BODY -----
    if (request.method == 'GET'):
        # RETURN RESPONSE
        return jsonify({
            "status": 200,
            "error": None,
            "message": None,
            "details": {
                "id": product.id,
                "title": product.title,
                "price": product.price,
                "description": product.description
            }
        })

    elif (request.method == 'PATCH'):
        # OWNERSHIP VALIDATION
        if (not product.user == current_user.id):
            return jsonify({
                "status": 400,
                "error": "OwnershipError",
                "message": "The product doesn't belong to current user or product id is invalid.",
                "details": { "product_id": id, },
            })

        # ACCESS JSON DATA
        data = request.json
        title = data.get('title')
        price = data.get('price')
        desc = data.get('desc')

        # UPDATE DETAILS AND UPDATE DB
        product.title = title
        product.price = price
        product.desc = desc
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            "status": 200,
            "error": None,
            "message": "Product updated successfully!",
            "details": {
                "title": title,
                "price": price,
                "description": desc,
            },
        }), 200

    elif (request.method == 'DELETE'):
        # OWNERSHIP VALIDATION
        if (not product.user == current_user.id):
            return jsonify({
                "status": 400,
                "error": "OwnershipError",
                "message": "The product doesn't belong to current user or product id is invalid.",
                "details": { "product_id": id, },
            }), 400

        # MARK PRODUCT AS DELETED AND UPDATE DB
        product.deleted = True
        db.session.commit()

        # RETURN RESPONSE
        return jsonify({
            "status": 200,
            "error": None,
            "message": "Product marked as deleted successfully!",
            "details": { "product_id": id, },
        }), 200


