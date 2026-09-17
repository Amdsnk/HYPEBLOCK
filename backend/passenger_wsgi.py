"""Passenger entry point for cPanel Python applications.

Set the cPanel Python application root to the backend directory and choose
this file as the startup file. Passenger speaks WSGI, while HYPEBLOCK is an
ASGI/FastAPI app, so a2wsgi bridges the two interfaces.
"""

import os
import sys

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from a2wsgi import ASGIMiddleware
from server import app as asgi_app

application = ASGIMiddleware(asgi_app)