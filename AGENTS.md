# Agent Guide — AlienCommons

> **Read this first.** Then read the closest nested `AGENTS.md` for the area you are editing.
> Keep changes small, intentional, and consistent with the surrounding code.

## What this is

AlienCommons is a community platform for Technical Minecraft players. It is a polyglot monorepo: a Django 6 backend, a Nuxt 4 frontend, an internal Fastify Markdown-rendering service, a TypeScript Markdown parser library, a DRF envelope library, three MkDocs documentation sites, and the Docker/observability wiring to run all of it.

## Repository map

```
aliencommons/
├── apps/
│   ├── backend/         Django 6 + DRF API. See apps/backend/AGENTS.md.
│   ├── frontend/        Nuxt 4 + Vue 3 + Pinia + Tailwind 4. See apps/frontend/AGENTS.md.
│   └── alienmark/       Internal Fastify service that renders Markdown via packages/alienmark.
├── packages/
│   ├── alienmark/        TypeScript Markdown parser + HTML renderer (published to GitHub Packages).
│   └── drf-std-response/ DRF response-envelope + exception-handler library used by the backend.
├── docs/                Three MkDocs sites (users, contributors, alienmark). See docs/AGENTS.md.
├── infra/compose/       Docker Compose files for dev / stg / pro / proxy.
├── o11y/                Grafana, Loki, Grafana Alloy configs.
├── make/                docker.mk + node.mk, included by the root Makefile.
├── env/                 Environment files for local Compose (.env.dev, .env.test).
└── .github/workflows/   CI/CD. ci.yml is the source of truth for verification gates.
```

## Nested guides (progressive disclosure)

Read the closest applicable guide **before** editing. The closest guide wins; this file only adds cross-cutting rules.

| Area | Guide | Read when |
|------|-------|-----------|
| Django backend | [`apps/backend/AGENTS.md`](apps/backend/AGENTS.md) | Touching anything under `apps/backend/` or `packages/drf-std-response/` |
| Nuxt frontend | [`apps/frontend/AGENTS.md`](apps/frontend/AGENTS.md) | Touching anything under `apps/frontend/` |
| AlienMark service | [`apps/alienmark/AGENTS.md`](apps/alienmark/AGENTS.md) | Touching the Fastify rendering service |
| AlienMark parser | [`packages/alienmark/AGENTS.md`](packages/alienmark/AGENTS.md) | Touching the parser library or its public API |
| DRF envelope lib | [`packages/drf-std-response/AGENTS.md`](packages/drf-std-response/AGENTS.md) | Touching the envelope / exception handler |
| Documentation | [`docs/AGENTS.md`](docs/AGENTS.md) | Touching anything under `docs/` |

If an area has no dedicated guide, follow the conventions already present in nearby code.

## Toolchains at a glance

| Concern | Tool | Pinning |
|---|---|---|
| Node workspace | pnpm 11 workspaces + Turbo | `package.json`, `pnpm-workspace.yaml`, `turbo.json` |
| Node quality/build | [Vite+](https://viteplus.dev) (`vp`) | root `vite.config.ts` (lint, format, type-aware checks) |
| Python (backend + docs) | uv workspaces | root `pyproject.toml`, `uv.lock` |
| Python lint | ruff | `apps/backend/ruff.toml` |
| Containers | Docker Compose | `infra/compose/*.yml`, driven via `make/` |
| CI | GitHub Actions | `.github/workflows/ci.yml` |

## Environments

Three environments. Do not encode environment-specific values in source.

- **`dev`** — local, via Docker Compose (`make dev-up`).
- **`stg`** — staging on AWS, mirrors production.
- **`pro`** — production on AWS. DNS for `aliencommons.com` is in Cloudflare.

## Common commands

Run from the repository root unless noted.

```bash
# Full local stack (Postgres, Redis, backend, workers, frontend, AlienMark, observability)
make dev-up

# Node workspace (matches CI `node` job)
pnpm install
pnpm run check              # Turbo: build deps, then per-package check
pnpm run knip               # advisory; pnpm run knip:strict to fail on findings

# Backend (matches CI `backend-*` jobs)
make dev-backend-test       # uses settings=test inside the backend-api container
make dev-backend-check      # python manage.py check inside the backend-api container
# Or locally inside apps/backend/:
#   uv run python manage.py test
#   uv run ruff check <app...> manage.py

# Docs subproject (matches CI `docs-*` jobs); run inside docs/<name>/
uv run mkdocs build --strict

# Single Node package via Turbo filter
pnpm turbo run check --filter=frontend
pnpm turbo run check --filter=alienmark
pnpm turbo run check --filter=alienmark-service
```

All other Make targets live in [`make/docker.mk`](make/docker.mk) and [`make/node.mk`](make/node.mk).

## Verification

Run the **smallest** check that covers your change. If a check cannot be run, say so in your final response.

| Change | Command |
|---|---|
| Any Node package (`apps/frontend`, `apps/alienmark`, `packages/alienmark`) | `pnpm run check` (or the package-specific filter) |
| Backend behavior | `uv run python manage.py test` from `apps/backend/`, or `make dev-backend-test` |
| Backend lint | `uv run ruff check <apps> manage.py` from `apps/backend/` |
| Docs site | `uv run mkdocs build --strict` from `docs/<name>/` |
| Unused-code audit (advisory) | `pnpm run knip` |

CI mirrors these in `.github/workflows/ci.yml`. If your change alters app names, settings modules, build commands, or verification steps, update the workflow too.

## Working rules

- **Read nearby code first.** Match the conventions already in the file or package you are touching.
- **Follow the closest nested guide.** It overrides anything generic here.
- **Don't widen scope.** No unrelated rewrites, no broad reformatting, no reverting user changes unless asked.
- **Keep secrets out of source.** No credentials, access keys, or bucket names in committed files. Prefer environment variables and IAM roles.
- **Treat migrations as part of model changes.** Add focused migrations when models change; don't edit applied migrations unless deliberately rewriting history.
- **Add or update tests when behavior changes** — even if nobody asked.
- **Keep generated artifacts out of diffs** (`.nuxt/`, `.output/`, `dist/`, `site/`, `staticfiles/`, `media/`, lockfile regeneration) unless the task is explicitly about them.

## Git

- Focused commits with clear messages.
- Feature work branches from `dev`. `main` is the release branch; releases are git tags.
- Don't encode release versions in `AGENTS.md`.
- Don't add a `Verification` section to PR descriptions unless explicitly asked.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **aliencommons** (2806 symbols, 5287 relationships, 128 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

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
