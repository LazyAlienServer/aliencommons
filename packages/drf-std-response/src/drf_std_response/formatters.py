from collections.abc import Mapping, Sequence

from rest_framework.exceptions import ErrorDetail

from .settings import get_setting


class ErrorFormatter:
    """
    Convert DRF error details into a flat, client-friendly error list.
    """

    default_code = "error"

    def __init__(self):
        self.separator = get_setting("NESTED_FIELD_SEPARATOR")
        self.non_field_errors_key = get_setting("NON_FIELD_ERRORS_KEY")

    def format_errors(self, detail):
        return [
            self.format_error(code=code, message=message, field=field)
            for code, message, field in self.iter_errors(detail)
        ]

    def format_error(self, *, code, message, field):
        return {
            "code": str(code or self.default_code),
            "message": str(message),
            "field": field,
        }

    def iter_errors(self, detail, path=None):
        path = [] if path is None else path

        if isinstance(detail, Mapping):
            yield from self.iter_mapping_errors(detail, path)
            return

        if self.is_error_sequence(detail):
            yield from self.iter_sequence_errors(detail, path)
            return

        yield self.get_error_code(detail), str(detail), self.format_path(path)

    def iter_mapping_errors(self, detail, path):
        for key, value in detail.items():
            if not path and key == "detail":
                child_path = path
            else:
                child_path = path if key is None else [*path, str(key)]
            yield from self.iter_errors(value, child_path)

    def iter_sequence_errors(self, detail, path):
        for index, value in enumerate(detail):
            if isinstance(value, Mapping):
                yield from self.iter_errors(value, [*path, str(index)])
            elif self.is_error_sequence(value):
                yield from self.iter_errors(value, path)
            else:
                yield self.get_error_code(value), str(value), self.format_path(path)

    def is_error_sequence(self, detail):
        return isinstance(detail, Sequence) and not isinstance(
            detail,
            (str, bytes, bytearray, ErrorDetail),
        )

    def get_error_code(self, detail):
        return getattr(detail, "code", self.default_code)

    def format_path(self, path):
        if not path:
            return None
        return self.separator.join(path)


def format_errors(detail):
    return ErrorFormatter().format_errors(detail)
