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

    try:
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
                    user=current_user.id,
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

    except Exception:
        flash("Something went wrong while syncing with your store.", "error")

    finally:
        return redirect(url_for('store.store_page'))

