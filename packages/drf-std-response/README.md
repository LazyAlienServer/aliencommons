# drf-std-response

Standard response envelope helpers for Django REST Framework.

```python
from drf_std_response import EnvelopeMixin, ServiceError
from rest_framework.viewsets import ModelViewSet


class ArticleViewSet(EnvelopeMixin, ModelViewSet):
    ...
```

`EnvelopeMixin` wraps successful DRF responses in a payload with `success`,
`message`, `code`, `data`, `errors`, and `meta`. Error responses can be wrapped
through the package exception handler:

```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "drf_std_response.exception_handlers.exception_handler",
}
```
