from os import environ

from opentelemetry.instrumentation.starlette import StarletteInstrumentor

environ.setdefault("DJANGO_ENV", "development")
environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")


def init_trace(service_name: str):
    import socket

    import MySQLdb
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,
    )
    from opentelemetry.instrumentation.aiohttp_client import (
        AioHttpClientInstrumentor,
    )
    from opentelemetry.instrumentation.dbapi import trace_integration
    from opentelemetry.instrumentation.django import DjangoInstrumentor
    from opentelemetry.instrumentation.grpc import (
        GrpcAioInstrumentorClient,
        GrpcAioInstrumentorServer,
    )
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.sdk.resources import HOST_NAME, SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    auth = environ.get("TRACE_AUTH", None)
    if auth is None:
        print("TRACE_AUTH is required when enable trace")
        return

    DjangoInstrumentor().instrument()
    DjangoInstrumentor().instrument(is_sql_commentor_enabled=True)
    RedisInstrumentor().instrument()
    AioHttpClientInstrumentor().instrument()
    trace_integration(MySQLdb, "connect", "mysql")

    grpc_server_instrumentor = GrpcAioInstrumentorServer()
    grpc_server_instrumentor.instrument()

    grpc_client_instrumentor = GrpcAioInstrumentorClient()
    grpc_client_instrumentor.instrument()

    resource = Resource(
        attributes={
            SERVICE_NAME: service_name,
            HOST_NAME: socket.getfqdn(),
        }
    )
    init_trace.set_tracer_provider(TracerProvider(resource=resource))
    init_trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint="http://tracing-analysis-dc-hz.aliyuncs.com:8090",
                headers=f"Authentication={auth}",
            )
        )
    )  # 通过 OTLPSpanExporter 上报Trace


def main():
    import django

    init_trace("paperpilot-backend-project")
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

StarletteInstrumentor().instrument_app(app)
