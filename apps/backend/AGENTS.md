# Backend Agent Guide

This directory contains the Django backend for AlienCommons. Keep backend changes small, intentional, and consistent with the existing Django/DRF style.

## Project Shape

- `backend/` contains Django project settings, URL configuration, ASGI, and WSGI entrypoints.
- `core/` contains shared response formatting, exception handling, pagination, viewset mixins, validators, middleware, and utility code.
- `users/`, `articles/`, `bookmarks/`, `tasks/`, and `logs/` are Django apps with their own models, services, views, serializers, admin, migrations, and tests where applicable.
- Runtime services include PostgreSQL, Redis/RQ task queues, Django sessions/cache, S3-backed media in staging/production, and the internal AlienMark rendering service.
- Tests live next to the app they cover under each app's `tests/` package.

## Working Rules

- Read nearby models, serializers, services, permissions, views, and tests before changing behavior.
- Preserve the existing service-layer pattern: keep business workflow logic out of views when there is already a service module for that domain.
- Use the local formatted response and exception handling utilities instead of returning ad hoc DRF responses from API views.
- Keep authentication, permission, session, email verification, article workflow, scheduler, and storage changes especially conservative; these are cross-cutting surfaces.
- Do not put secrets, access keys, bucket names that should be environment-specific, or local environment values into source files.
- Prefer environment variables for deployment-specific settings. EC2/ECS IAM roles should provide AWS credentials where possible; do not add static AWS keys to settings.
- Treat migrations as part of model changes. Add focused migrations when models change, and avoid editing existing applied migrations unless the project is still deliberately rewriting history.
- Keep generated/static/media artifacts out of code changes unless the task is explicitly about those assets.
- Once add a new app, check whether it exists in AGENTS.md and in relevant GitHub Actions. If applicable, add it to them.

## Verification

- Use the smallest relevant checks for the change.
- For normal backend behavior changes, prefer:

  ```bash
  uv run python manage.py test
  ```

- For lint-sensitive changes, prefer:

  ```bash
  uv run ruff check articles backend core logs tasks users manage.py
  ```

- If local dependencies or services make a check impossible, say exactly what was not run and why.
- After any backend change, inspect the backend GitHub workflows under `.github/workflows/` and decide whether they need updates. In particular, check backend lint, backend tests, and backend API docs workflows when dependencies, commands, settings modules, app names, generated schema behavior, or verification steps change.

## Settings And Environments

- `backend.settings.base` is the shared production-like foundation.
- `backend.settings.dev`, `backend.settings.stg`, and `backend.settings.pro` layer deployment-specific behavior on top of base.
- `backend.settings.test` is intentionally independent and should remain fast, deterministic, and isolated from PostgreSQL, Redis, S3, and external services unless a test explicitly opts into an integration path.
- Be careful when touching storage settings: static files and media files have different lifecycles. Static files are deploy artifacts; media files are user/runtime data.

## API And Data Contracts

- Keep API responses wrapped in the project-standard envelope with `success`, `message`, `code`, `data`, `errors`, and `meta`.
- Keep serializer validation errors and service-layer errors compatible with the custom exception handler.
- Preserve existing URL naming and router conventions unless the change explicitly requires a versioned API contract change.
- Add or update tests when behavior, permissions, workflow state transitions, task scheduling, storage behavior, or API contracts change.
