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

    ai_tone = db.Column(db.String, default='Mentor')
    ai_creativity = db.Column(db.Integer, default=0)
    ai_lang = db.Column(db.String, default="English")

    total_credits = db.Column(db.Integer, default=50)
    left_credits = db.Column(db.Integer, default=50)

    plan = db.Column(db.String, default="Free")
    renewal_date = db.Column(db.Date, default=date.today() + timedelta(days=30))

    captions = db.relationship('Caption', backref='author', lazy=True)
    headlines = db.relationship('Headline', backref='author', lazy=True)
    saved = db.relationship('SavedGen', backref='author', lazy=True)
    payments = db.relationship('Payment', backref='author', lazy=True)
    products = db.relationship('Product', backref='author', lazy=True)
    orders = db.relationship('Order', backref='author', lazy=True)