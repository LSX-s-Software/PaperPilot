from os import environ

from starlette.applications import Starlette

from server import settings
from server.urls import routes
from server.utils.logging_handler import init_logging

environ.setdefault("DJANGO_ENV", "development")

init_logging()

app = Starlette(debug=settings.DEBUG, routes=routes)
