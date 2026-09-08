"""
Routers management file for the Project.

Manages all routers in the applications.
"""

# ? IMPORTS
from flask import Flask
from .app import app
from .auth import auth
from .billing import billing
from .store import store
from .newsletter import news
from .docs import docs
from .legal import legal

# * FUNCTION TO BIND ALL ROUTERS TO THE SERVER
def bind_routers(server: Flask) -> None:
    """
    Binds all routers to the server.

    :param server: Flask instance of the Project.

    ## Usage
    ```python
        from flask import Flask
        from routers import bind_routers
        
        server = Flask(__name__)
        bind_routers(server)
    ```
    """

    server.register_blueprint(app)
    server.register_blueprint(auth)
    server.register_blueprint(billing)
    server.register_blueprint(store)
    server.register_blueprint(docs)
    server.register_blueprint(news)
    server.register_blueprint(legal)