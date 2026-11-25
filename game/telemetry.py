import logging

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


OTEL_ENDPOINT = (
    "otel-collector.opentelemetry.svc.cluster.local:4317"
)


# --------------------------------------------------
# Shared resource
# --------------------------------------------------

resource = Resource.create(
    {
        "service.name": "sre-runner",
        "service.version": "3.0",
        "deployment.environment": "minikube",
    }
)


# --------------------------------------------------
# Tracing
# --------------------------------------------------

tracer_provider = TracerProvider(
    resource=resource
)

trace_exporter = OTLPSpanExporter(
    endpoint=OTEL_ENDPOINT,
    insecure=True,
)

tracer_provider.add_span_processor(
    BatchSpanProcessor(
        trace_exporter
    )
)

trace.set_tracer_provider(
    tracer_provider
)

tracer = trace.get_tracer(
    "sre-runner"
)


# --------------------------------------------------
# Logging
# --------------------------------------------------

logger_provider = LoggerProvider(
    resource=resource
)

log_exporter = OTLPLogExporter(
    endpoint=OTEL_ENDPOINT,
    insecure=True,
)

logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        log_exporter
    )
)

set_logger_provider(
    logger_provider
)


otel_logging_handler = LoggingHandler(
    level=logging.INFO,
    logger_provider=logger_provider,
)


logger = logging.getLogger(
    "sre-runner"
)

logger.setLevel(
    logging.INFO
)

logger.addHandler(
    otel_logging_handler
)

logger.propagate = False


def shutdown_telemetry():
    tracer_provider.force_flush()
    logger_provider.force_flush()

    tracer_provider.shutdown()
    logger_provider.shutdown()
