# Node Tooling

AlienCommons uses three Node workspace tools together:

- **pnpm workspaces** define the package graph and install dependencies.
- **Turbo** runs cross-package tasks in dependency order.
- **Vite+** provides the package-level commands for checks, formatting, tests, and TypeScript library or service builds.

They are layered rather than interchangeable. pnpm answers "which packages exist and how do they depend on each other?", Turbo answers "which package task must run before another?", and Vite+ answers "what does this package's check, format, test, or pack command actually do?"

## Package Graph

The Node workspace is declared in `pnpm-workspace.yaml`:

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

At the moment, the relevant Node packages are:

| Package | Location | Role |
| --- | --- | --- |
| `frontend` | `apps/frontend` | Nuxt 4 frontend application |
| `alienmark-service` | `apps/alienmark` | Internal Fastify Markdown rendering service |
| `alienmark` | `packages/alienmark` | TypeScript Markdown parser and HTML renderer |

Both `frontend` and `alienmark-service` depend on the local `alienmark` package:

```json
"alienmark": "workspace:*"
```

That `workspace:*` dependency is the source of truth for the Node dependency graph. pnpm links the local package during install, and Turbo uses the same workspace graph to decide upstream task order.

## Task Orchestration

Turbo is the workspace task orchestrator. The root `package.json` exposes aggregate commands such as:

```bash
pnpm run check
pnpm run build
pnpm run test
pnpm run typecheck
```

Those commands call `turbo run ...`, and `turbo.json` defines how task dependencies behave. For example, `build`, `check`, `test`, and `typecheck` depend on upstream package builds:

```json
"build": {
  "dependsOn": ["^build"],
  "outputs": ["dist/**", ".nuxt/**", ".output/**"]
},
"check": {
  "dependsOn": ["^build"]
}
```

The `^build` dependency means "run the `build` task of workspace dependencies first." In practice:

```text
alienmark#build
  -> frontend#check
  -> alienmark-service#check
```

and:

```text
alienmark#build
  -> frontend#build
  -> alienmark-service#build
```

This keeps dependency ordering in one place instead of repeating manual sequences such as "build `alienmark`, then build the service" in Make targets, CI jobs, or Dockerfiles.

## Package Commands

Vite+ is the package-level tool. Each Node package should expose the same basic script names where applicable:

```json
{
  "check": "vp check",
  "check:fix": "vp check --fix",
  "lint:check": "vp lint",
  "lint:fix": "vp lint --fix",
  "style:check": "vp fmt --check",
  "style:fix": "vp fmt"
}
```

Packages still use the tool that best matches their build target:

| Package | Build command | Why |
| --- | --- | --- |
| `frontend` | `nuxt build` | Nuxt application build |
| `alienmark-service` | `vp pack src/server.ts --format esm --dts false` | ESM Node service bundle |
| `alienmark` | `vp pack` | TypeScript library package with declarations |

So Vite+ does not replace pnpm or Turbo. It standardizes the commands that Turbo runs inside each package.

## Root Entrypoints

Use root scripts for normal development and CI:

```bash
pnpm run check      # all package checks through Turbo
pnpm run build      # all package builds through Turbo
pnpm run test       # JavaScript tests through Turbo
pnpm run typecheck  # TypeScript checks through Turbo
```

Single-package convenience scripts are available when the scope is known:

```bash
pnpm run frontend:check
pnpm run alienmark:build
pnpm run alienmark-service:check
```

These root convenience scripts should prefer Turbo for tasks that need dependency ordering, especially `build`, `check`, `test`, and `typecheck`.

Direct `pnpm --filter <name> ...` commands are still useful for long-running dev servers:

```bash
pnpm --filter frontend dev
pnpm --filter alienmark-service dev
```

Development servers are intentionally persistent and usually do not need the full workspace task graph.

## Maintenance Rules

When adding or changing a Node package:

1. Add it under a path included by `pnpm-workspace.yaml`.
2. Use `workspace:*` for local package dependencies.
3. Add standard Vite+ scripts such as `check`, `lint:check`, `style:check`, and `typecheck` when applicable.
4. Let root scripts and Make targets call Turbo instead of manually sequencing package dependencies.
5. Update `turbo.json` when a new task has outputs, needs upstream builds, is persistent, or should not be cached.
6. Update CI path filters when a new root-level Node tooling file can affect the Node job.

The intended mental model is:

```text
pnpm workspace = package map and dependency installation
Turbo          = cross-package task graph
Vite+          = package-level quality and build commands
```

Keeping those responsibilities separate makes the workspace easier to scale as more apps and packages are added.
