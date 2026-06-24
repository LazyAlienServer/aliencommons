from .exceptions import ServiceError
from .formatters import ErrorFormatter, format_errors
from .mixins import EnvelopeMixin
from .responses import build_payload, format_response


def exception_handler(*args, **kwargs):
    from .exception_handlers import exception_handler as _exception_handler

    return _exception_handler(*args, **kwargs)


__all__ = [
    "EnvelopeMixin",
    "ErrorFormatter",
    "ServiceError",
    "build_payload",
    "exception_handler",
    "format_errors",
    "format_response",
]


def __getattr__(name):
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
