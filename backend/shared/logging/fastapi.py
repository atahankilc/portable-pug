import uuid

from .context import bind_request_context, clear_request_context


def _parse_traceparent(header: str | None) -> str | None:
    if not header:
        return None
    parts = header.split("-")
    if len(parts) < 2:
        return None
    trace_id = parts[1]
    if len(trace_id) == 32 and trace_id != "0" * 32:
        return trace_id
    return None


class RequestContextMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {
            k.decode("latin-1").lower(): v.decode("latin-1")
            for k, v in scope["headers"]
        }
        request_id = headers.get("x-request-id") or uuid.uuid4().hex
        trace_id = _parse_traceparent(headers.get("traceparent")) or request_id

        tokens = bind_request_context(request_id, trace_id)

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"].append(
                    (b"x-request-id", request_id.encode("latin-1"))
                )
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            clear_request_context(tokens)
