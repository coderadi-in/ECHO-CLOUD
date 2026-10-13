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
    # CHECK IF USER HAS AN INTEGRATED STORE
    check_store_integration()

    # SCRAPE STORE
    old_products = [prod.tolist() for prod in current_user.products]
    scraped = scrape_store()
    scraped_list = scraped.values.tolist()

    # ITERATE OVER ALL OLD PRODUCTS
    scraped_ids = set()
    for new_product in scraped_list:
        prod_id = "".join(c for c in new_product[0] if c.isdigit())
        if (prod_id):
            scraped_ids.add(int(prod_id))

    for old_product in old_products:
        if (old_product[0] not in scraped_ids):
            product = Product.query.get(old_product[0])
            if (product):
                db.session.delete(product)

    # ITERATE OVER ALL SCRAPED PRODUCTS
    for product in scraped_list:
        prod_id = "".join(char for char in product[0] if char.isdigit())
        prod_price = "".join(char for char in product[2] if char.isdigit())

        # CHECK IF THEY'RE TOTALLY NEW
        prod_instance = Product.query.filter(
            Product.user == current_user.id,
            Product.id == int(prod_id)
        ).first()

        if (not prod_instance):
            new_product = Product(
                id=int(prod_id),
                title=product[1],
                price=product[2],
                desc=product[3]
            )
            db.session.add(new_product)

        else:
            # CHECK IF THEY'RE PATCHED OR IDENTICAL
            prod_instance.title = product[1] if prod_instance.title != product[1] else prod_instance.title
            prod_instance.price = int(prod_price) if prod_instance.price != int(prod_price) else prod_instance.price
            prod_instance.desc = product[3] if prod_instance.title != product[3] else prod_instance.desc

    # COMMIT & RETURN
    db.session.commit()
    flash("Your store is synced with the application.", "store")
    return redirect(url_for('store.store_page'))
'''
[
    ['ID: 100001', 'Classic Cotton T-Shirt', '3200', 'Soft breathable cotton tee perfect for everyday casual wear.'],
    ['ID: 100002', 'Ceramic Coffee Mug', '4500', 'Sturdy 350ml ceramic mug with a comfortable easy-grip handle.'],
    ['ID: 100003', 'Notebook A5 Ruled', '460', 'Compact A5 notebook with 120 ruled pages and durable cover.'],
    ['ID: 100004', 'Stainless Water Bottle', '2400', 'Insulated 500ml bottle keeps drinks cold or hot for hours.']
]
'''

# # SYNC STORE ROUTE
# @store.route('/sync')
# @login_required
# @limiter.limit("30 per minute")
# def sync_store():
#     check_store_integration()

#     # DELETE ALL OLD PRODUCTS
#     for product in current_user.products:
#         db.session.delete(product)

#     # SCRAPE USER'S STORE
#     products = scrape_store()
    
#     if (isinstance(products, bool)):
#         flash("Unable to sync.", "error")
#         return redirect(url_for('store.store_page'))
    
#     product_list = products.values.tolist()

#     if (len(product_list) == 0):
#         flash("Couldn't extract products from store.", "error")
#         return redirect(url_for('store.store_page'))

#     # ADD NEW PRODUCTS TO DB
#     for product in product_list:
#         price = "".join(char for char in product[2] if char.isdigit())
#         id = "".join(char for char in product[0] if char.isdigit())

#         new_product = Product(
#             id=int(id),
#             user=current_user.id,
#             title=product[1],
#             price=float(price),
#             desc=product[3]
#         )

#         db.session.add(new_product)
    
#     # COMMIT AND RETURN
#     db.session.commit()
#     flash("Your store is synced with the application.", "store")
#     return redirect(url_for('store.store_page'))