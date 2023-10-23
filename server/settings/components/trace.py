import MySQLdb
import sentry_sdk
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.grpc import (
    GrpcAioInstrumentorClient,
    GrpcAioInstrumentorServer,
)
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from sentry_sdk.integrations.django import DjangoIntegration

from server.settings.util import config

SENTRY_DSN = config("SENTRY_DSN", None)

SENTRY_ENABLE = config("SENTRY_ENABLE", False, bool)

if SENTRY_ENABLE:
    assert SENTRY_DSN, "SENTRY_DSN is required when SENTRY_ENABLE is True"
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.01,
        debug=config("DEBUG", False),
        environment=config("DJANGO_ENV", "production"),
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=False,
    )

JAEGER_HOST = config("JAEGER_HOST", None)

provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME: "paperpilot-backend-user"})
)
trace.set_tracer_provider(provider)

# create a JaegerExporter
jaeger_exporter = JaegerExporter(
    agent_host_name="tracing-analysis-dc-hz.aliyuncs.com",
    agent_port=8090,
)

# Create a BatchSpanProcessor and add the exporter to it
span_processor = BatchSpanProcessor(jaeger_exporter)

# add to the tracer
trace.get_tracer_provider().add_span_processor(span_processor)

DjangoInstrumentor().instrument(is_sql_commentor_enabled=True)
RedisInstrumentor().instrument()

# trace_integration(MySQLdb, "connect", "mysql")

grpc_server_instrumentor = GrpcAioInstrumentorServer()
grpc_server_instrumentor.instrument()

grpc_client_instrumentor = GrpcAioInstrumentorClient()
grpc_client_instrumentor.instrument()
