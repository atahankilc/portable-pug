from contextvars import ContextVar, Token
from dataclasses import dataclass

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)


@dataclass
class RequestContextTokens:
    request_id: Token
    trace_id: Token


def bind_request_context(request_id: str, trace_id: str) -> RequestContextTokens:
    return RequestContextTokens(
        request_id=request_id_var.set(request_id),
        trace_id=trace_id_var.set(trace_id),
    )


def clear_request_context(tokens: RequestContextTokens) -> None:
    request_id_var.reset(tokens.request_id)
    trace_id_var.reset(tokens.trace_id)
