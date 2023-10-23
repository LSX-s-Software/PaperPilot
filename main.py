from os import environ

from starlette.applications import Starlette
from opentelemetry.instrumentation.starlette import StarletteInstrumentor

from server import settings
from server.urls import routes
from server.utils.logging_handler import init_logging

environ.setdefault("DJANGO_ENV", "development")

def init_trace(service_name: str):
    import socket

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,
    )
    from opentelemetry.instrumentation.aiohttp_client import (
        AioHttpClientInstrumentor,
    )
    from opentelemetry.instrumentation.grpc import (
        GrpcAioInstrumentorClient,
    )
    from opentelemetry.sdk.resources import HOST_NAME, SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    auth = environ.get("TRACE_AUTH", None)
    if auth is None:
        print("TRACE_AUTH is required when enable trace")
        return

    AioHttpClientInstrumentor().instrument()

    grpc_client_instrumentor = GrpcAioInstrumentorClient()
    grpc_client_instrumentor.instrument()

    resource = Resource(
        attributes={
            SERVICE_NAME: service_name,
            HOST_NAME: socket.getfqdn(),
        }
    )
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint="http://tracing-analysis-dc-hz.aliyuncs.com:8090",
                headers=f"Authentication={auth}",
            )
        )
    )  # 通过 OTLPSpanExporter 上报Trace


init_logging()
init_trace("paperpilot-backend-file")

app = Starlette(debug=settings.DEBUG, routes=routes)

StarletteInstrumentor.instrument_app(app)
