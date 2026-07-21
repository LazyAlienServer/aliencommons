# Frontend Agent Guide — `apps/frontend/`

This directory is intentionally a minimal Nuxt 4 scaffold. It contains no product features yet.

## Stack

- Nuxt 4
- Vue 3
- Vue Router
- Pinia
- Tailwind CSS 4
- AlienMark workspace library
- TypeScript
- Vite through Nuxt

## Structure

```text
app/app.vue       Minimal root component
app/assets/css/   Global Tailwind CSS entrypoint
public/           Static starter assets
nuxt.config.ts    Minimal Nuxt configuration
package.json      Frontend scripts and runtime dependencies
tsconfig.json     Nuxt-generated project references
Dockerfile        Production Nitro/Node container image
```

Do not restore code from the previous Vue application unless the user explicitly asks for it. Add future product code incrementally using Nuxt 4 conventions.

## Verification

Run from the repository root:

```bash
pnpm turbo run check --filter=frontend
pnpm turbo run typecheck --filter=frontend
pnpm turbo run build --filter=frontend
docker build -f apps/frontend/Dockerfile -t aliencommons-frontend .
```
