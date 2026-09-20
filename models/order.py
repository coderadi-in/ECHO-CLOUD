"""
Order database management file for the Project.

Manages the orders table.
"""

# ? IMPORTS
from plugins import *
from datetime import date


# ! MODEL INIT
class Order(db.Model):
    """
    Order database model.
    Stores the data of orders made by clients.

    ```python
        order = Order(
            user=current_user.id
        )
    ```
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    ordered_on = db.Column(db.Date, default=date.today())
    status = db.Column(db.String(20), default='unrecognized') # ['accepted', 'rejected', 'unrecognized']