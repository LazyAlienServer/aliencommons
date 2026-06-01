# Agent Guide

Keep changes small, intentional, and consistent with the existing project.

## Project Shape

This is a monorepo. The main areas are:

- `apps/` for deployable applications.
- `packages/` for reusable packages.
- `docs/` for documentation.
- `infra/`, `o11y/`, and `make/` for operations and tooling.

Prefer the conventions already present in the area you are editing.

## Nested Guides

Read the closest applicable `AGENTS.md` before editing in these areas:

| Area | Guide |
|------|-------|
| `apps/backend/` | `apps/backend/AGENTS.md` |
| `docs/` (and each docs subproject) | `docs/AGENTS.md` |

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
- Check for nested `AGENTS.md` files and follow the closest applicable instructions.
- Do not rewrite unrelated files or reformat broad areas without a reason.
- Do not remove or revert user changes unless explicitly asked.
- Keep secrets, credentials, and local environment files out of commits.
- Use existing scripts, Make targets, and package commands when available.
- Add or update tests when the change affects behavior.

## Verification

Run the smallest relevant checks for the change. If a check cannot be run, mention that in the final response.

| Area | Command | Notes |
|------|---------|-------|
| Node workspace (frontend, alienmark, alienmark-service) | `pnpm run check` | Aggregate gate; matches the CI `node` job. |
| Node single package | `pnpm --filter <name> check` | Runs lint, typecheck, and style for one package. |
| Backend (in `apps/backend/`) | `uv run python manage.py test` | See `apps/backend/AGENTS.md` for ruff and per-app guidance. |
| Backend via Compose | `make dev-backend-test` / `make dev-backend-check` | Uses `infra/compose/docker-compose.dev.yml`. |
| Docs subproject (in `docs/<name>/`) | `uv run mkdocs build --strict` | Matches the CI `docs-*` jobs. |

For the full local stack, use `make dev-up`. Other Make targets live in `make/docker.mk` and `make/node.mk`.

## Git

- Use focused commits and clear commit messages.
- Feature work should normally branch from `dev`. `main` is the release branch.
- Production releases are represented by git tags. Do not encode release versions in this file.
- Do not include a `Verification` section in pull request descriptions unless the user explicitly asks for one.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **aliencommons** (2970 symbols, 5535 relationships, 106 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/aliencommons/context` | Codebase overview, check index freshness |
| `gitnexus://repo/aliencommons/clusters` | All functional areas |
| `gitnexus://repo/aliencommons/processes` | All execution flows |
| `gitnexus://repo/aliencommons/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
