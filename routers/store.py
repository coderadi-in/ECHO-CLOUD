"""
Application store routes management file for the Project.

Manages the routes of store.
"""

# ==================================================
# SETUP
# ==================================================

# ? IMPORTS
from flask import Blueprint, render_template, redirect, url_for, request
from plugins import *
from models import *

# ! ROUTER INIT
store = Blueprint('store', __name__, url_prefix='/store')

# * FUNCTION TO CHECK IF USER HAS INTEGRATED HIS STORE
def check_store_integration():
    """
    Checks if store is integrated or not
    """
    if (not current_user.site_url):
        flash("You have't integrated your store yet.", 'error')
        return redirect(url_for('app.dashboard'))

# ==================================================
# ROUTES
# ==================================================

# & STORE ROUTE
@store.route('/')
@login_required
@limiter.limit("30 per minute")
def store_page():
    check_store_integration()    
    return render_template('pages/store.html')

# & SYNC STORE ROUTE
@store.route('/sync')
@login_required
@limiter.limit("30 per minute")
def sync_store():
    check_store_integration()

    # DELETE ALL OLD PRODUCTS
    for product in current_user.products:
        db.session.delete(product)

    # CHECK IF USER HAS INTEGRATED ANY STORE
    if (not current_user.site_url):
        db.session.commit()
        flash("You haven't integrated any site URL.", "error")
        return redirect(url_for('store.store_page'))

    # SCRAPE USER'S STORE
    products = scrape_store()
    
    if (isinstance(products, bool)):
        flash("Unable to sync.", "error")
        return redirect(url_for('store.store_page'))
    
    product_list = products.values.tolist()

    if (len(product_list) == 0):
        flash("Couldn't extract products from store.", "error")
        return redirect(url_for('store.store_page'))

    # ADD NEW PRODUCTS TO DB
    for product in product_list:
        price = "".join(char for char in product[2] if char.isdigit())
        id = "".join(char for char in product[0] if char.isdigit())

        new_product = Product(
            id=int(id),
            user=current_user.id,
            title=product[1],
            price=float(price),
            desc=product[3]
        )

        db.session.add(new_product)
    
    # COMMIT AND RETURN
    db.session.commit()
    flash("Your store is synced with the application.", "store")
    return redirect(url_for('store.store_page'))