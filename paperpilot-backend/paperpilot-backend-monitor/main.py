from os import environ

from opentelemetry.instrumentation.starlette import StarletteInstrumentor

from server.utils.trace import init_trace

environ.setdefault("DJANGO_ENV", "development")
environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")


def main():
    init_trace("paperpilot-backend-monitor")
    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

    from server.urls import routes
    from server.utils.logging_handler import init_logging

    init_logging()

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=[
                "*",
            ],
        )
    ]

    return Starlette(routes=routes, middleware=middleware)


app = main()

StarletteInstrumentor().instrument_app(app)
