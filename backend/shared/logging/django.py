import uuid

from .context import bind_request_context, clear_request_context
from .fastapi import _parse_traceparent


class DjangoRequestContextMiddleware:
    """Django analogue of the FastAPI middleware: binds request_id/trace_id
    into contextvars so `shared.logging.formatter.JsonFormatter` picks them up."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        trace_id = (
            _parse_traceparent(request.headers.get("traceparent")) or request_id
        )
        tokens = bind_request_context(request_id, trace_id)
        try:
            response = self.get_response(request)
        finally:
            clear_request_context(tokens)
        response["X-Request-ID"] = request_id
        return response
