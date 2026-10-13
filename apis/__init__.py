"""
API Routers management file for the Project.

Manages all API routers in the applications.
"""

# ? IMPORTS
from flask import Flask
from .admin import admin
from .ai import ai
from .auth import auth
from .data_exporter import data_exporter
from .matrices import matrices
from .orders import orders
from .payments import payments
from .products import products
from .user import user

# * FUNCTION TO BIND ALL APIs TO THE SERVER
def bind_apis(server: Flask):
    """
    Binds all API routers to the server.

    :param server: Flask instance of the Project.

    ## Usage
    ```python
        from flask import Flask
        from apis import bind_apis

        server = Flask(__name__)
        bind_apis(server)
    ```
    """

    server.register_blueprint(admin)
    server.register_blueprint(ai)
    server.register_blueprint(auth)
    server.register_blueprint(data_exporter)
    server.register_blueprint(orders)
    server.register_blueprint(matrices)
    server.register_blueprint(payments)
    server.register_blueprint(products)
    server.register_blueprint(user)