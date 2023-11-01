#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


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
        GrpcAioInstrumentorServer,
    )
    # from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.sdk.resources import HOST_NAME, SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    auth = os.environ.get("TRACE_AUTH", None)
    if auth is None:
        print("TRACE_AUTH is required when enable trace")
        return

    # RedisInstrumentor().instrument()
    AioHttpClientInstrumentor().instrument()

    grpc_server_instrumentor = GrpcAioInstrumentorServer()
    grpc_server_instrumentor.instrument()

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


def main():
    os.environ.setdefault("DJANGO_ENV", "development")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
    init_trace("paperpilot-backend-translation")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
