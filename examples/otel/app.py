from apiflask import APIFlask
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.semconv.resource import ResourceAttributes

app = APIFlask(__name__, title='apiflask-otel', version='1.0.0')


def configure_trace(app: APIFlask):
    """initialize OpenTelemetry based on the provided settings.

    Args:
        app (APIFlask): APIFlask instance
    """
    resource = Resource(
        attributes={
            ResourceAttributes.SERVICE_NAME: app.title,
            ResourceAttributes.SERVICE_VERSION: app.version,
        }
    )
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    FlaskInstrumentor().instrument_app(app)


configure_trace(app=app)


@app.get('/')
def index():
    span_ctx = trace.get_current_span().get_span_context()
    print(f'trace id: {span_ctx.trace_id}, span id: {span_ctx.span_id}')
    return {'trace_id': span_ctx.trace_id, 'span_id': span_ctx.span_id}
