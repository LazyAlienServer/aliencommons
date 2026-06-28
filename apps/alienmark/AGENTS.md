# AlienMark Service Agent Guide — `apps/alienmark/`

Internal HTTP service that renders Markdown to HTML using the `alienmark` workspace package (see [`packages/alienmark/AGENTS.md`](../../packages/alienmark/AGENTS.md)). Called by the Django backend.

## Stack

- **Fastify 5** — HTTP server.
- **TypeScript** — strict, ESM.
- **alienmark** (`workspace:*`) — the actual parser/renderer. This service is a thin HTTP wrapper around `renderMarkdown`.
- Built with `vp pack src/server.ts --format esm --dts false` → emits `dist/server.mjs`.

## Surface

Single source file: `src/server.ts`. Two routes:

| Method | Path | Body | Returns | Notes |
|---|---|---|---|---|
| `GET` | `/health` | — | `{ ok: true, service: "alienmark" }` | Liveness probe. |
| `POST` | `/render-html` | `{ markdown: string }` | `{ html: string }` | Renders Markdown via `renderMarkdown`. Body limit 1 MiB. Fastify JSON schema validates request and response. |

Config via env:

- `PORT` (default `8787`) — must be an integer in `(0, 65535]`; invalid values throw.
- `HOST` (default `0.0.0.0`).

The server uses top-level `await` on `app.listen` — it's an ESM entrypoint, not a long-running importable module.

## Commands

| Action | Command |
|---|---|
| Dev (watch) | `pnpm --filter alienmark-service dev` (`tsx watch src/server.ts`) |
| Build | `pnpm turbo run build --filter=alienmark-service` → `dist/server.mjs` |
| Start (built) | `pnpm --filter alienmark-service start` (`node dist/server.mjs`) |
| Full check | `pnpm turbo run check --filter=alienmark-service` |
| Typecheck | `pnpm turbo run typecheck --filter=alienmark-service` (`tsc --noEmit`) |
| Lint | `pnpm turbo run lint:check --filter=alienmark-service` |
| Format check | `pnpm turbo run fmt:check --filter=alienmark-service` |

## Conventions

- **Keep the surface intentionally small.** This service exists to move Markdown rendering out of the Python process; don't grow it into a general-purpose API.
- **No business logic here.** Parsing behavior lives in `packages/alienmark`. If the renderer needs a new feature, add it there and ship a new lib version — don't patch around it in the service.
- **Validate at the Fastify schema layer** (JSON schema on route definitions), as the existing routes already do.
- **ESM + top-level await are expected** — don't refactor to CommonJS or wrap `app.listen` in a function unless there's a concrete reason.
- **TypeScript strict.** No `any`, no `@ts-ignore`.

## Rules

- Match the existing style in `src/server.ts`.
- Don't commit `dist/`.
- Coordinate changes with the backend caller (see [`apps/backend/AGENTS.md`](../backend/AGENTS.md)) and the parser library (see [`packages/alienmark/AGENTS.md`](../../packages/alienmark/AGENTS.md)) when changing the request/response contract.

## Verification

```bash
pnpm turbo run check --filter=alienmark-service      # vp check (lint + format + type-aware)
pnpm turbo run typecheck --filter=alienmark-service  # tsc --noEmit
```

For behavioral changes, also exercise the running service:

```bash
pnpm turbo run build --filter=alienmark-service && pnpm --filter alienmark-service start
# in another terminal:
curl -s localhost:8787/health
curl -s -X POST localhost:8787/render-html -H 'content-type: application/json' -d '{"markdown":"# hi"}'
```
