"""
Products database management file for the Project.

Manages the product table.
"""

# ? IMPORTS
from plugins import *

# ! MODEL INIT
class Product(db.Model):
    """
    Products database model.
    Stores the data of products.

    ```python
        product = Product(
            user=current_user.id,
            title="<product_title>",
            price=354.34,
            desc="<product_desc>"
        )
    ```
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    desc = db.Column(db.TEXT, nullable=False)

    orders = db.relationship('Order', backref='product', lazy=True)