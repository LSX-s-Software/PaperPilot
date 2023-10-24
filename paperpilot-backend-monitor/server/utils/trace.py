import os


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
        GrpcInstrumentorClient,
    )
    from opentelemetry.sdk.resources import HOST_NAME, SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    auth = os.environ.get("TRACE_AUTH", None)
    if auth is None:
        print("TRACE_AUTH is required when enable trace")
        return

    AioHttpClientInstrumentor().instrument()

    grpc_server_instrumentor = GrpcAioInstrumentorServer()
    grpc_server_instrumentor.instrument()

    grpc_client_instrumentor = GrpcInstrumentorClient()
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
