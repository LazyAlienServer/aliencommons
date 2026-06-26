# Backend Agent Guide — `apps/backend/`

Django 6 + DRF API for AlienCommons. Python 3.14, ASGI via Daphne/Channels. Depends on the workspace package `drf-std-response` (see [`packages/drf-std-response/AGENTS.md`](../../packages/drf-std-response/AGENTS.md)).

## Project shape

- `backend/` — Django project: `settings/`, `urls.py`, `asgi.py`, `wsgi.py`.
- `backend/settings/` — `base.py` (prod-like foundation) + `dev.py`, `stg.py`, `pro.py`, `test.py` overlays.
- `core/` — shared code: response/pagination/viewset mixins, validators, middleware, model mixins, fields, signals, test helpers.
- The other top-level Python packages are Django apps (see table below). Each app typically has `models.py`, `serializers.py`, `services.py`, `views.py`, `permissions.py`, `admin.py`, `migrations/`, and a `tests/` package.
- `manage.py` — entrypoint; default `DJANGO_SETTINGS_MODULE` is `backend.settings.dev`.

### Apps

| App | Domain |
|-----|--------|
| `users` | Users, sessions, email verification, subscriptions |
| `articles` | Articles, published articles, collections, article workflow |
| `bookmarks` | Bookmark folders and article bookmarks |
| `comments` | Article comments and replies |
| `notifications` | Notification events, fan-out deliveries, inbox APIs |
| `posts` | Community posts and related content |
| `reactions` | Like/dislike targets and user reactions |
| `reports` | Content and user moderation reports |
| `tasks` | Scheduled/background task definitions |
| `core` | Shared utilities, responses, permissions, test helpers |
| `logs` | (Referenced by ruff/lint scope; treat as app-shaped module) |

> The ruff lint scope in CI is exactly: `articles bookmarks comments backend core logs notifications posts reactions reports tasks users manage.py`. When you add a new app, add it here, in `.github/workflows/ci.yml` (`backend-lint` step), and in any app-list settings (e.g. `INSTALLED_APPS`, router registries).

## Runtime services

- **PostgreSQL 18** — primary data store.
- **Redis 8** — django-redis cache, Django sessions, RQ broker.
- **RQ workers** via `django-tasks-rq` — queues `default`, `email`, `maintenance` (see `make dev-backend-runrqworker`).
- **Scheduler** — `make dev-backend-runscheduler` → `python manage.py runscheduler`.
- **AlienMark** — internal Fastify Markdown rendering service (`apps/alienmark/`); backend calls it over HTTP.
- **Media storage** — local filesystem in `dev`/`test`; S3-compatible via `django-storages` in `stg`/`pro` when configured. Static files are deploy artifacts; media files are user/runtime data — they have different lifecycles.

## Commands

Run inside `apps/backend/` unless noted. The Compose equivalents run inside the `backend-api` container.

| Action | Local | Compose |
|---|---|---|
| Tests | `uv run python manage.py test` (or `--settings=backend.settings.test`) | `make dev-backend-test` |
| System check | `uv run python manage.py check` | `make dev-backend-check` |
| Lint | `uv run ruff check articles bookmarks comments backend core logs notifications posts reactions reports tasks users manage.py` | (run locally) |
| Make migrations | `uv run python manage.py makemigrations` | `make dev-backend-makemigrations` |
| Apply migrations | `uv run python manage.py migrate` | `make dev-backend-migrate` |
| Shell | `uv run python manage.py shell` | `make dev-backend-shell` |
| Create superuser | `uv run python manage.py createsuperuser` | `make dev-backend-createsuperuser` |
| Init scheduled tasks | `uv run python manage.py init_tasks` | `make dev-backend-init-tasks` |
| Run scheduler | `uv run python manage.py runscheduler` | `make dev-backend-runscheduler` |
| Run RQ worker | `uv run python manage.py rqworker default email maintenance` | `make dev-backend-runrqworker` |
| Bash in container | — | `make dev-backend-bash` |

## Settings and environments

- `backend.settings.base` — shared production-like foundation. Layer environment-specific behavior on top of it, not by editing base.
- `backend.settings.dev` / `stg` / `pro` — deployment overlays.
- `backend.settings.test` — **intentionally independent.** Must stay fast, deterministic, and isolated from PostgreSQL, Redis, S3, and external services unless a test explicitly opts into an integration path. Don't add network/IO dependencies to `test` casually.
- `ruff.toml` allows `F403`/`F405` only inside `backend/settings/{dev,pro,stg}.py` (star-import settings files).
- Keep secrets/AWS credentials out of settings. EC2/ECS IAM roles should provide AWS creds in hosted environments — do not add static AWS keys.

## Architecture rules

- **Service layer is authoritative for workflow logic.** When an app has a `services.py` (or `services/`), put business/workflow logic there — not in views or serializers. Views orchestrate; services decide.
- **Use the standard response envelope.** API responses go through the project-standard envelope (`success`, `message`, `code`, `data`, `errors`, `meta`) provided by `drf-std-response`. Don't return ad-hoc DRF `Response` shapes from API views. See the DRF envelope guide for `EnvelopeMixin`, `ServiceError`, and the exception handler.
- **Permissions are explicit.** Use DRF permission classes; don't gate writes inside view bodies.
- **Cross-cutting surfaces are conservative edits**: authentication, permissions, sessions, email verification, article workflow state machines, scheduler, and storage. Read the surrounding code before changing them.

## Migrations

- Add a focused migration whenever models change. One logical change per migration.
- Never edit an applied migration unless deliberately rewriting history.
- Don't squash or rename migrations casually — downstream deployments and CI depend on the linear history.

## Tests

- Tests live in each app's `tests/` package, next to the code they cover.
- Default test runner: Django's built-in runner (`manage.py test`) under `backend.settings.test`.
- Add or update tests whenever behavior, permissions, workflow transitions, task scheduling, storage, or API contracts change — even if not explicitly requested.
- Keep tests hermetic: use fixtures/factories, don't depend on `dev`/`stg` data or external HTTP.

## API and data contracts

- Responses wrapped in the standard envelope via `EnvelopeMixin` / `format_success_response`.
- Errors normalized through the `drf_std_response` exception handler. Raise `ServiceError(detail=..., code=...)` from service code for client-facing errors.
- Preserve existing URL naming and DRF router conventions unless the change is an intentional API version bump.
- Serializer validation errors must stay compatible with the custom exception handler (don't bypass DRF validation).

## Verification

Run the smallest relevant check. If a check can't run, say so in the final response.

```bash
# Tests (matches CI backend-tests job)
uv run python manage.py test

# Lint (matches CI backend-lint job scope exactly)
uv run ruff check articles bookmarks comments backend core logs notifications posts reactions reports tasks users manage.py

# System check
uv run python manage.py check
```

After any backend change, inspect `.github/workflows/ci.yml` and decide whether the `backend-lint` or `backend-tests` jobs (or deployment/docs workflows) need updates — e.g. when adding/removing apps, changing settings modules, build commands, or verification steps.
