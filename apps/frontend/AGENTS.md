# Frontend Agent Guide — `apps/frontend/`

Nuxt 4 + Vue 3 + Pinia + Tailwind CSS 4. TypeScript, strict. Consumes the workspace package `alienmark` (see [`packages/alienmark/AGENTS.md`](../../packages/alienmark/AGENTS.md)) for Markdown rendering.

## Stack

- **Nuxt 4** (`nuxt@^4.4`) — app shell, file-based routing, SSR, auto-imports.
- **Vue 3** (`vue@^3.5`) — Composition API + `<script setup>`.
- **Pinia** (`pinia@^3` via `@pinia/nuxt`) — state management.
- **Tailwind CSS 4** (`tailwindcss@^4.3` via `@tailwindcss/vite`) — styling. Main stylesheet: `app/assets/css/main.css`.
- **vue-router** — Nuxt-managed.
- **vue-toastification** — toast UI.
- **axios** + **js-cookie** — HTTP and cookie handling.
- **vite-svg-loader** — `import Svg from "~/assets/.../foo.svg"` gives a Vue component.

> The repo's Vue/Nuxt conventions are enforced by user-installed skills. Load `vue-best-practices`, `vue`, `vue-router-best-practices`, and `nuxt` before non-trivial Vue/Nuxt work, and `vue-testing-best-practices` for tests.

## App layout

```
app/
├── app.vue                Root component.
├── assets/css/main.css    Tailwind entrypoint (referenced by vite.config.ts sortTailwindcss).
├── components/            Auto-imported global components (AppHeader, AppFooter, BaseModal, HeroSection...).
├── composables/           Auto-imported composables (use* functions).
├── features/              Feature-scoped modules (articles/, users/, profile/, api/).
├── layouts/               Nuxt layouts (default.vue).
├── pages/                 File-based routing ([...slug].vue, index.vue, login.vue, register.vue, logout.vue, theme.vue, cookie-policy.vue...).
├── stores/                Pinia stores (theme.ts, user.ts).
└── utils/                 Auto-imported utilities (cookie.ts, error.ts).
```

Nuxt auto-imports `composables/`, `utils/`, and `components/`. Don't add manual imports for those — Nuxt's resolver already handles them.

## Commands

| Action | Command |
|---|---|
| Dev server | `pnpm run frontend:dev` (or `make frontend-dev`) |
| Full check (lint + format + type-aware) | `pnpm run frontend:check` |
| Typecheck only | `pnpm run frontend:typecheck` (`vue-tsc --noEmit`) |
| Lint | `pnpm run frontend:lint` |
| Format check | `pnpm run frontend:fmt` |
| Production build | `pnpm run frontend:build` (`nuxt build`) |
| Preview built app | `pnpm run frontend:preview` |

The check pipeline runs through Turbo with `dependsOn: ["^build"]`, so the `alienmark` workspace dependency is built first. Run `pnpm run check` from the root to check the whole Node workspace in dependency order.

## Conventions

- **Composition API + `<script setup>` only.** Do not add Options API code.
- **TypeScript everywhere.** `vue-tsc --noEmit` is part of the check gate.
- **No `any` / `@ts-ignore`.** The repo's Vite+ config warns on `typescript/no-explicit-any`; type things properly.
- **Use Pinia stores** in `app/stores/` for cross-component state. Define stores with the composition (setup) style already in use.
- **Tailwind first.** Reuse existing classes and components; the main stylesheet is the formatting anchor — don't introduce competing style systems.
- **HTTP via axios** in `app/features/api/`. Wrap API calls in feature modules, not ad-hoc calls inside components.
- **Markdown rendering** uses the `alienmark` workspace package — don't hand-roll HTML from Markdown.
- **Routing is file-based.** Add pages under `app/pages/`; don't manually register routes.

## Rules

- Match the conventions already in the file or feature module you're touching.
- Keep changes small; don't restructure `features/`, `stores/`, or `components/` en passant.
- Don't commit generated artifacts (`.nuxt/`, `.output/`, `dist/`).
- Update English and Chinese doc/content together when relevant (see [`docs/AGENTS.md`](../../docs/AGENTS.md)).

## Verification

```bash
pnpm run frontend:check      # = vp check (lint + format + type-aware)
pnpm run frontend:typecheck  # vue-tsc only
```

If a UI/UX change is non-trivial, verify visually in the dev server (`pnpm run frontend:dev`) in addition to the check gate.
