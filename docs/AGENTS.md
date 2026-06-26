# Documentation Agent Guide — `docs/`

Three independent MkDocs sites. Each is its own uv workspace package and has its own `mkdocs.yml`, `pyproject.toml`, and `docs/` content tree.

## Sites

| Subproject | Package name | Site name | CI build job | CI deploy workflow |
|---|---|---|---|---|
| `docs/users/` | `aliencommons-users-docs` | AlienCommons User Guide | `docs-users` | (none) |
| `docs/contributors/` | `aliencommons-contributors-docs` | AlienCommons Docs | `docs-contributors` | `.github/workflows/contributors-docs-deploy.yml` |
| `docs/alienmark/` | `aliencommons-alienmark-docs` | AlienMark Docs | `docs-alienmark` | `.github/workflows/alienmark-docs-deploy.yml` |

## Stack (all three sites)

- MkDocs `1.6.1`, Material for MkDocs `9.7.6`, `mkdocs-static-i18n` `1.3.1` (exact pins, Python `>=3.14`).
- `mkdocs-static-i18n` configured with `docs_structure: suffix`, locales `en` (default, `build: true`) and `zh` (`build: true`).
- Theme: Material, default language `en`. Each locale can supply `nav_translations`.

## Filename convention (i18n suffix)

Because `docs_structure: suffix` is on, every translatable page exists as two files:

```
docs/<site>/docs/<page>.en.md
docs/<site>/docs/<page>.zh.md
```

`mkdocs.yml` nav entries use the bare stem (e.g. `index.md`, `syntax.md`, `product/roles.md`). The plugin resolves the per-locale file at build time.

## Writing rules

- **Update both `*.en.md` and `*.zh.md` together.** They must be equivalent in meaning; wording need not be literal.
- **Keep nav in sync.** Adding, moving, or removing a page requires updating that site's `mkdocs.yml` `nav:` block, in both languages if `nav_translations` are present.
- **Don't invent.** No features, commands, or deployment steps that don't exist in the project. Cross-check against source (`apps/`, `packages/`) when documenting behavior.
- **Match the existing page style**: heading depth, tone, terminology.
- **Don't commit generated `site/` output** unless the task is explicitly about it.
- Small, focused edits; no broad rewrites.

## Commands

Run inside the relevant `docs/<site>/` directory.

```bash
# Live preview
uv run mkdocs serve

# Strict build (matches CI; fails on warnings, missing pages, broken links)
uv run mkdocs build --strict
```

CI runs each docs job from inside `docs/<name>/` via `uv sync --project ../.. --locked --package aliencommons-<name>-docs` then `mkdocs build --strict`. Run the same `--strict` build locally before pushing.

## Cross-references

- AlienMark syntax docs (`docs/alienmark/docs/syntax.*.md`) must stay in sync with the parser's actual supported subset in [`packages/alienmark/`](../../packages/alienmark/AGENTS.md). When you change supported syntax, update the parser, its tests, and these docs together.
- Contributor docs reference the backend/frontend/architecture — keep them consistent with the code in [`apps/backend/`](../../apps/backend/AGENTS.md) and [`apps/frontend/`](../../apps/frontend/AGENTS.md).

## Verification

```bash
# From docs/<site>/ — strict build matches the CI docs-* jobs
uv run mkdocs build --strict
```

If the build warns, treat it as a failure — CI runs with `--strict`.
