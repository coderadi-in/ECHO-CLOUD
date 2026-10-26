"""
User database management file for the Project.

Manages the user table.
"""

# ? IMPORTS
from plugins import *
from datetime import date

# ! MODEL INIT
class User(db.Model, UserMixin):
    """
    User database model.
    Stores the data of user.

    ```python
        user = User(
            name="coderadi",
            email="adi@coderadi.in",
            password="<password>",
            site_url="coderadi.in",
        )
    ```
    """
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    last_generation = db.Column(db.Float)

    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    site_url = db.Column(db.String)

    total_credits = db.Column(db.Integer, default=50)
    left_credits = db.Column(db.Integer, default=50)

    last_plan = db.Column(db.String, default="free")
    current_plan = db.Column(db.String, default="free")
    renewal_date = db.Column(db.Date, default=date.today() + relativedelta(months=1))

    captions = db.relationship('Caption', backref='author', lazy=True)
    headlines = db.relationship('Headline', backref='author', lazy=True)
    barcode_sheets = db.relationship('BarcodeSheet', backref='author', lazy=True)
    saved = db.relationship('SavedGen', backref='author', lazy=True)
    payments = db.relationship('Payment', backref='author', lazy=True)
    products = db.relationship('Product', backref='author', lazy=True)
    orders = db.relationship('Order', backref='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'site_url': self.site_url,
            'total_credits': self.total_credits,
            'left_credits': self.left_credits,
            'last_plan': self.last_plan,
            'current_plan': self.current_plan,
            'renewal_date': self.renewal_date.isoformat() if self.renewal_date else None,
        }