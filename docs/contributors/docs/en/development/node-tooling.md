# Node Tooling

AlienCommons uses three Node workspace tools together:

- **pnpm workspaces** define the package graph and install dependencies.
- **Turbo** runs cross-package tasks in dependency order.
- **Vite+** provides the package-level commands for checks, formatting, tests, and TypeScript library or service builds.

They are layered rather than interchangeable. pnpm answers "which packages exist and how do they depend on each other?", Turbo answers "which package task must run before another?", and Vite+ answers "what does this package's check, format, test, or pack command actually do?"

Knip is also available as an advisory maintenance tool. It does not replace any of the three layers above, and it is not part of the required `pnpm run check` gate. Its job is to report unused files, exports, dependencies, and catalog entries when a maintainer wants to clean up the workspace.

## Package Graph

The Node workspace is declared in `pnpm-workspace.yaml`:

```yaml
packages:
  - "apps/*"
  - "packages/*"
  - "!packages/drf-std-response"
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
  "fmt:check": "vp fmt --check",
  "fmt:fix": "vp fmt",
  "lint:check": "vp lint",
  "lint:fix": "vp lint --fix"
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
pnpm run knip       # advisory unused-code and unused-dependency report
```

Use Turbo filters directly when the scope is known:

```bash
pnpm turbo run check --filter=frontend
pnpm turbo run build --filter=alienmark
pnpm turbo run check --filter=alienmark-service
```

Do not add root wrapper scripts such as `frontend:check`; Turbo's filter syntax is the package-scoped interface.

Direct `pnpm --filter <name> ...` commands are still useful for long-running dev servers:

```bash
pnpm --filter frontend dev
pnpm --filter alienmark-service dev
```

Development servers are intentionally persistent and usually do not need the full workspace task graph.

Knip is intentionally separate from the aggregate check:

```bash
pnpm run knip         # report findings but exit successfully
pnpm run knip:strict  # report findings and return a non-zero exit code
```

Use the default advisory command during cleanup work, dependency pruning, or before larger refactors. Use the strict command only when you deliberately want unused-code findings to block a local run.

## Maintenance Rules

When adding or changing a Node package:

1. Add it under a path included by `pnpm-workspace.yaml`.
2. Use `workspace:*` for local package dependencies.
3. Add standard Vite+ scripts such as `check`, `fmt:check`, `lint:check`, and `typecheck` when applicable.
4. Let root scripts and Make targets call Turbo instead of manually sequencing package dependencies.
5. Update `turbo.json` when a new task has outputs, needs upstream builds, is persistent, or should not be cached.
6. Update CI path filters when a new root-level Node tooling file can affect the Node job.
7. Update `knip.jsonc` when a new framework entrypoint, generated type file, or intentionally retained dependency needs to be understood by the unused-code audit.

The intended mental model is:

```text
pnpm workspace = package map and dependency installation
Turbo          = cross-package task graph
Vite+          = package-level quality and build commands
Knip           = advisory unused-code and dependency audit
```

Keeping those responsibilities separate makes the workspace easier to scale as more apps and packages are added.
