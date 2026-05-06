# Agent Guide

Keep changes small, intentional, and consistent with the existing project.

## Project Shape

This is a monorepo. The main areas are:

- `apps/` for deployable applications.
- `packages/` for reusable packages.
- `docs/` for documentation.
- `infra/`, `o11y/`, and `make/` for operations and tooling.

Prefer the conventions already present in the area you are editing.

## Tech Stacks

- Monorepo tooling: pnpm workspaces, Make targets, Docker Compose, and GitHub Actions.
- Frontend: Nuxt 4, Vue 3, TypeScript, Tailwind CSS 4, Pinia, and the local `alienmark` workspace package.
- Backend: Python 3.14, Django 6, Django REST Framework, Django Channels/Daphne, django-filter, django-cors-headers, and environs.
- Backend persistence and runtime services: PostgreSQL, Redis, django-redis cache, Django sessions, RQ task workers via `django-tasks-rq`, and Pillow for image processing.
- Media and storage: local filesystem storage in development/test paths, with S3-compatible storage through `django-storages` for hosted environments when configured.
- Markdown rendering: `packages/alienmark` is a TypeScript Markdown parser/HTML renderer; `apps/alienmark` exposes it as an internal Fastify service used by the Django backend.
- Documentation: MkDocs, Material for MkDocs, and `mkdocs-static-i18n`.
- Operations and observability: Docker, Traefik labels in hosted compose files, Grafana, Loki, and Grafana Alloy.
- Hosted environments use AWS infrastructure conventions and Cloudflare DNS for `aliencommons.com`.

## Environments

The project uses three environments:

- `dev` is local development.
- `stg` is hosted on AWS and should mirror production as closely as practical.
- `pro` is the production environment and is hosted on AWS.

DNS is managed in Cloudflare for `aliencommons.com`.

## Working Rules

- Read the nearby code before changing it.
- Do not rewrite unrelated files or reformat broad areas without a reason.
- Do not remove or revert user changes unless explicitly asked.
- Keep secrets, credentials, and local environment files out of commits.
- Use existing scripts, Make targets, and package commands when available.
- Add or update tests when the change affects behavior.

## Verification

Run the smallest relevant checks for the change. If a check cannot be run, mention that in the final response.

## Git

- Use focused commits and clear commit messages.
- Feature work should normally branch from the active development branch.
- Production releases should be represented by tags, not by editing this file.
