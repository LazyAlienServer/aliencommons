# drf-std-response

Standard response envelopes for Django REST Framework.

`drf-std-response` wraps successful DRF responses and exception responses in one
consistent payload:

```json
{
  "success": true,
  "message": "listed",
  "code": "listed",
  "data": [],
  "errors": null,
  "meta": {
    "request_id": "req-1",
    "timestamp": "2026-03-17T10:00:00Z"
  }
}
```

## Quickstart

Use `EnvelopeMixin` before the DRF viewset class:

```python
from drf_std_response import EnvelopeMixin
from rest_framework.viewsets import ModelViewSet


class ArticleViewSet(EnvelopeMixin, ModelViewSet):
    ...
```

Register the exception handler:

```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "drf_std_response.exception_handlers.exception_handler",
}
```

Raise `ServiceError` from service-layer code when the error should become a
client-facing API response:

```python
from drf_std_response import ServiceError


raise ServiceError(detail="Article cannot be published", code="invalid_state")
```

## Success Responses

`EnvelopeMixin` wraps successful DRF `Response` objects in `finalize_response`.
It works with DRF's native mixins and viewsets, including `ModelViewSet` and
`ReadOnlyModelViewSet`.

Default action messages and codes are provided for common viewset actions:

| Action | message | code |
| --- | --- | --- |
| `list` | `listed` | `listed` |
| `retrieve` | `retrieved` | `retrieved` |
| `create` | `created` | `created` |
| `update` | `updated` | `updated` |
| `partial_update` | `updated` | `updated` |
| `destroy` | `deleted` | `deleted` |

For custom actions, use `format_success_response` when you need a specific
message or code:

```python
return self.format_success_response(
    message="article submitted",
    code="article_submitted",
    data=serializer.data,
)
```

## Error Responses

Errors use the same outer envelope. Validation, client, service, and server
errors are normalized into a flat `errors` list:

```json
{
  "success": false,
  "message": "Validation failed",
  "code": "validation_error",
  "data": null,
  "errors": [
    {
      "code": "required",
      "message": "This field is required.",
      "field": "title"
    }
  ],
  "meta": {
    "request_id": null,
    "timestamp": null
  }
}
```

Nested serializers and list serializers are flattened into dotted field paths:

```json
[
  {
    "code": "unsupported",
    "message": "Unsupported address",
    "field": "shipping_address.non_field_errors"
  },
  {
    "code": "invalid",
    "message": "Enter a valid email address.",
    "field": "recipients.1.email"
  }
]
```

## Customization

Customize the exception handler or formatter with Django settings:

```python
DRF_STD_RESPONSE = {
    "EXCEPTION_HANDLER_CLASS": "myapp.api.MyExceptionHandler",
    "EXCEPTION_FORMATTER_CLASS": "myapp.api.MyErrorFormatter",
    "NESTED_FIELD_SEPARATOR": ".",
    "NON_FIELD_ERRORS_KEY": "non_field_errors",
}
```

Formatter classes can subclass `ErrorFormatter`:

```python
from drf_std_response import ErrorFormatter


class MyErrorFormatter(ErrorFormatter):
    def format_error(self, *, code, message, field):
        return {
            "code": code,
            "detail": message,
            "attr": field,
        }
```

Handler classes can subclass `ExceptionHandler`:

```python
from drf_std_response.exception_handlers import ExceptionHandler


class MyExceptionHandler(ExceptionHandler):
    def convert_known_exceptions(self, exc):
        ...
```

## Acknowledgements

The structured error-normalization design in this package is inspired by
[`drf-standardized-errors`](https://github.com/ghazi-git/drf-standardized-errors).
