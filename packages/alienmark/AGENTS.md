# AlienMark Parser Agent Guide — `packages/alienmark/`

TypeScript Markdown parser and HTML renderer. Published to GitHub Packages as `@lazyalienserver/alienmark`. Consumed by `apps/frontend` (workspace) and `apps/alienmark` (workspace, HTTP service). Syntax docs live in `docs/alienmark/`.

This is a **published library**: the public API surface is a stability contract.

## Public API

From `src/index.ts`:

```ts
// High-level
export function renderMarkdown(markdown: string, options?: ParseOptions): string;
export function parseMarkdown(markdown: string, options?: ParseOptions): DocumentNode;

// Lower-level
export { parse, renderHtml };
export type * from "./ast/nodes.js";  // DocumentNode, ParseOptions, and all AST node types
```

- `renderMarkdown` = `renderHtml(parse(markdown, options))`.
- `parseMarkdown` returns the structured AST (`DocumentNode`).
- `parse` and `renderHtml` are the lower-level entrypoints, also exported.
- All AST node types are re-exported from `src/ast/nodes.ts`.

> Treat anything exported from `src/index.ts` as the public surface. Don't rename, reorder, or change signatures of these exports without bumping the package version and coordinating downstream (`apps/frontend`, `apps/alienmark`, and external consumers via GitHub Packages).

## Supported Markdown subset

AlienMark is **not** full CommonMark. It intentionally supports only what AlienCommons needs:

- Headings `#` through `####`.
- Paragraphs.
- Strong emphasis `**text**` / `__text__`; emphasis `*text*` / `_text_`.
- Inline code with backticks.
- Links `[label](url)`; images `![alt](url)`.
- Fenced code blocks (triple backticks).
- Blockquotes (`>`).
- Single-level ordered and unordered lists.
- Horizontal rules (`---`, `***`, `___`).

When adding syntax, extend the AST in `src/ast/nodes.ts`, parse it in `src/parser/`, render it in `src/renderer/`, document it in `docs/alienmark/docs/syntax.{en,zh}.md`, and add tests in `test/`.

## Source layout

```
src/
├── index.ts            Public re-exports.
├── ast/nodes.ts        AST node types + ParseOptions + DocumentNode.
├── parser/
│   ├── parse.ts        Block parser entrypoint.
│   └── inline.ts       Inline parser (emphasis, code, links, images).
└── renderer/
    └── render-html.ts  AST → HTML.
test/
└── alienmark.test.ts   Vitest tests (run via `vp test run`).
```

## Toolchain

- **Build**: `vp pack` → ESM `dist/index.mjs` + `dist/index.d.mts`.
- **Tests**: Vitest (`vp test run`).
- **Typecheck**: `tsc --noEmit` under `tsconfig.json` — note strict flags: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `isolatedModules`.
- Module: `NodeNext`. Target: `ESNext`. Use real ESM imports with `.js` specifiers (e.g. `./parser/parse.js`) — `verbatimModuleSyntax` requires `import type` for type-only imports.

## Commands

| Action | Command |
|---|---|
| Build (lib) | `pnpm turbo run build --filter=alienmark` |
| Dev (watch) | `pnpm --filter alienmark dev` |
| Tests | `pnpm turbo run test --filter=alienmark` (`vp test run`) |
| Full check | `pnpm turbo run check --filter=alienmark` |
| Typecheck | `pnpm turbo run typecheck --filter=alienmark` (`tsc --noEmit`) |
| Lint | `pnpm turbo run lint:check --filter=alienmark` |
| Format check | `pnpm turbo run fmt:check --filter=alienmark` |

## Rules

- **Public API is stable.** Bump `version` in `package.json` (currently `0.1.x`) on any breaking change; coordinate with `apps/frontend` and `apps/alienmark` and external consumers.
- **No `any`.** `exactOptionalPropertyTypes` is on — model optional fields precisely; don't smuggle `undefined` into required positions.
- **`.js` import specifiers are mandatory** (NodeNext + `verbatimModuleSyntax`). Type-only imports must use `import type`.
- **Always update both `test/` and `docs/alienmark/docs/syntax.{en,zh}.md`** when supported syntax changes (see [`docs/AGENTS.md`](../../docs/AGENTS.md) on keeping EN/ZH in sync).
- **Don't commit `dist/`.**
- Match existing parser/renderer conventions; don't introduce a CommonMark-compliant reimplementation unless that's the explicit task.

## Verification

```bash
pnpm turbo run test --filter=alienmark       # Vitest
pnpm turbo run check --filter=alienmark      # vp check (lint + format + type-aware)
pnpm turbo run typecheck --filter=alienmark  # tsc --noEmit
```

CI publishes this package from the `main` branch via `.github/workflows/alienmark-package-publish.yml`. Don't change the publish workflow's package name, registry, or version source without coordinating.
