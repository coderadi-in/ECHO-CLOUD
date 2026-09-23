"""
Promo database management file for the Project.

Manages the promo table.
"""

# ? IMPORTS
from plugins import *

# & ASSOCIATION TABLE
promo_code_users = db.Table(
    'promo_code_users',
    db.Column('promo_code_id', db.Integer, db.ForeignKey('promo_code.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# ! MODEL INIT
class PromoCode(db.Model):
    """
    Products database model.
    Stores the data of products.

    ```python
        product = Product(
            code="<ECHO_PROMO>",
            sponsor="<TEAM_ECHO>",
            limit=500,
            expiry=<date(2026, 07, 14)>
        )
    ```
    """

    __tablename__ = "promo_code"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), nullable=False)
    sponsor = db.Column(db.String)
    users = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer)
    discount = db.Column(db.Float)
    available_plans = db.Column(db.JSON, default=['standard', 'pro', 'ultra'])
    limit = db.Column(db.Integer)
    expiry = db.Column(db.Date)

    users_list = db.relationship(
        'User',
        secondary=promo_code_users,
        lazy=True
    )