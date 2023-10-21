from os import environ

environ.setdefault("DJANGO_ENV", "development")
environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")


def main():
    import django

    django.setup()
    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

    from server import settings
    from server.urls import routes
    from server.utils.logging_handler_uvicorn import init_logging

    init_logging()

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=[
                "*",
            ],
        )
    ]

    return Starlette(debug=settings.DEBUG, routes=routes, middleware=middleware)


app = main()
