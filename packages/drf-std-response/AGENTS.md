# DRF Std Response Agent Guide — `packages/drf-std-response/`

Django REST Framework response-envelope and exception-handler library. Pinned to Django 6 + DRF 3.17. Consumed by `apps/backend` via the uv workspace (see [`apps/backend/AGENTS.md`](../../apps/backend/AGENTS.md)).

The full user-facing reference is in [`README.md`](README.md). This guide is the agent-facing short form: read it before editing the library.

## What it does

- Wraps every DRF API response in a single standardized envelope.
- Normalizes exceptions through one exception handler so success and error responses share the same shape.
- Flattens nested serializer validation errors into stable, dotted field paths.

## Envelope shape

```jsonc
{
  "success": true,         // false on error
  "message": "articles listed",  // human-facing action message
  "code": "OK",            // machine-facing status code
  "data":    { /* ... */ },// payload on success
  "errors":  [ /* ... */ ],// structured errors on failure
  "meta":    { /* ... */ } // pagination / extra metadata
}
```

## Wiring (backend side)

In DRF settings:

```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "drf_std_response.exception_handlers.exception_handler",
    # ...your defaults
}
```

On viewsets, place `EnvelopeMixin` **before** the DRF viewset class in MRO:

```python
class ArticleViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    ...
```

## Public API surface (treat as stable)

- `EnvelopeMixin` — DRF viewset mixin that produces the envelope.
- `ServiceError(detail, code)` — exception for client-facing service-layer errors. Raise from service code; the handler converts it to a structured error response.
- `format_success_response(message, code, data)` — builds a success envelope. Useful when you need to construct one outside the mixin.
- Default action messages (used by the mixin unless overridden):
  - `list` → "retrieved" + "listed"
  - `retrieve` → "retrieved"
  - `create` → "created"
  - `update` / `partial_update` → "updated"
  - `destroy` → "deleted"

## Customization points (Django settings)

Under the `DRF_STD_RESPONSE` setting:

| Key | Default | Purpose |
|---|---|---|
| `EXCEPTION_HANDLER_CLASS` | library default | Swap the exception handler class. |
| `EXCEPTION_FORMATTER_CLASS` | library default | Swap the error formatter class. |
| `NESTED_FIELD_SEPARATOR` | `"."` | Joins nested serializer field paths in error keys. |
| `NON_FIELD_ERRORS_KEY` | `"non_field_errors"` | Key for cross-form / non-field errors. |

Extension points for downstream subclassing:

- `ErrorFormatter.format_error(*, code, message, field)` — per-error formatting.
- `ExceptionHandler.convert_known_exceptions(exc)` — map non-DRF exceptions to DRF types before formatting.

Inspired by `drf-standardized-errors`; do not reimplement that package wholesale — extend via the hooks above.

## Rules

- **The envelope shape is a public contract.** Adding fields is potentially breaking for external API consumers; removing or renaming fields is breaking. Bump `version` in `pyproject.toml` and coordinate the backend bump.
- **Pin to the workspace's Django/DRF versions.** `pyproject.toml` uses `django==6.0.6` and `djangorestframework==3.17.1` (exact, add-bounds policy). Don't loosen these casually.
- **Don't smuggle ad-hoc response shapes past the handler.** Backend views should rely on `EnvelopeMixin` / `format_success_response`, not hand-built `Response` payloads.
- Match the existing code style; keep the module importable with `python>=3.14`.
- Keep the README's examples in sync when public API changes.

## Verification

This is a library, so verification is mostly: it imports cleanly under the pinned Django/DRF, and the backend that consumes it still passes.

```bash
# From repo root — verify the backend still imports and tests pass after lib edits:
uv sync --project apps/backend --locked --dev --package aliencommons-backend
(cd apps/backend && uv run --project ../.. --package aliencommons-backend python manage.py check)
(cd apps/backend && uv run --project ../.. --package aliencommons-backend python manage.py test)
```

If you add unit tests inside this package, run them directly:

```bash
uv run --package drf-std-response pytest   # only if a pytest config/test suite exists here
```
