from os import environ

from server.utils.logging_handler_uvicorn import init_logging

environ.setdefault("DJANGO_ENV", "development")
environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")


def main():
    import django

    django.setup()
    from starlette.applications import Starlette

    from server import settings
    from server.urls import routes

    init_logging()
    return Starlette(debug=settings.DEBUG, routes=routes)


app = main()
