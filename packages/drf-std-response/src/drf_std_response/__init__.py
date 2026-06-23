from .exceptions import ServiceError
from .mixins import EnvelopeMixin
from .responses import build_payload, format_response

__all__ = [
    "EnvelopeMixin",
    "ServiceError",
    "build_payload",
    "exception_handler",
    "format_response",
]


def __getattr__(name):
    if name == "exception_handler":
        from .exception_handlers import exception_handler

        return exception_handler
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
