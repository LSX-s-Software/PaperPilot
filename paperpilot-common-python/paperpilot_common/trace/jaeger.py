from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def register_to_jaeger(name: str, host: str):
    """
    注册服务到jaeger，这样就可以发送tracer相关信息到jaeger服务器
    Args:
        name:  注册的服务明
        host:   jaeger地址

    Returns: TracerProvider

    """

    host = host.split(":")
    addr = host[0]
    if len(host) > 1:
        port = int(host[1])
    else:
        port = 6831

    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: name}))
    trace.set_tracer_provider(provider)

    # create a JaegerExporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=addr,
        agent_port=port,
    )

    # Create a BatchSpanProcessor and add the exporter to it
    span_processor = BatchSpanProcessor(jaeger_exporter)

    # add to the tracer
    trace.get_tracer_provider().add_span_processor(span_processor)
