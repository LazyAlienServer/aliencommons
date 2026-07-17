# Documentation Agent Guide — `docs/`

Three independent Zensical sites. Each is its own uv workspace package and has a default English `zensical.toml`, a Chinese `zensical.zh.toml`, a `pyproject.toml`, and a `docs/` content tree.

## Sites

| Subproject | Package name | Site name | CI build job | CI deploy workflow |
|---|---|---|---|---|
| `docs/users/` | `aliencommons-user-guide` | AlienCommons User Guide | `docs-users` | (none) |
| `docs/contributors/` | `aliencommons-contributor-docs` | AlienCommons Docs | `docs-contributors` | `.github/workflows/contributors-docs-deploy.yml` |
| `docs/alienmark/` | `alienmark-docs` | AlienMark Docs | `docs-alienmark` | `.github/workflows/alienmark-docs-deploy.yml` |

## Stack and configuration (all three sites)

- Zensical is exactly pinned in each site's `pyproject.toml` (Python `>=3.14`).
- `zensical.toml` builds English from `docs/en/` into `site/`.
- `zensical.zh.toml` builds Chinese from `docs/zh/` into `site/zh/`.
- Each configuration sets its own theme language and navigation labels. Both expose the English/Chinese language selector.
- Always build English first, then Chinese. The English build owns `site/`; the Chinese build adds the `site/zh/` subtree.

## Bilingual content convention

Every translatable page exists at the same relative path below both language roots:

```
docs/<site>/docs/en/<page>.md
docs/<site>/docs/zh/<page>.md
```

Links stay language-local because each build has its own `docs_dir`. Use ordinary relative Markdown links such as `syntax.md` or `product/roles.md`; do not add language suffixes or prefixes.

## Writing rules

- **Update matching files under `docs/en/` and `docs/zh/` together.** They must be equivalent in meaning; wording need not be literal.
- **Keep nav in sync.** Adding, moving, or removing a page requires updating `nav` in both `zensical.toml` and `zensical.zh.toml`.
- **Don't invent.** No features, commands, or deployment steps that don't exist in the project. Cross-check against source (`apps/`, `packages/`) when documenting behavior.
- **Match the existing page style**: heading depth, tone, terminology.
- **Don't commit generated `site/` output** unless the task is explicitly about it.
- Small, focused edits; no broad rewrites.

## Commands

Run inside the relevant `docs/<site>/` directory.

```bash
# Live preview
uv run zensical serve

# Preview Chinese on a separate port
uv run zensical serve --config-file zensical.zh.toml --dev-addr localhost:8001

# Strict build (matches CI; fails on warnings, missing pages, broken links)
uv run zensical build --strict
uv run zensical build --strict --config-file zensical.zh.toml
```

CI runs each docs job from inside `docs/<name>/` via `uv sync --project ../.. --locked --package <package-name>`, then runs both strict Zensical builds in the order above. Run the same commands locally before pushing.

## Cross-references

- AlienMark syntax docs (`docs/alienmark/docs/{en,zh}/syntax.md`) must stay in sync with the parser's actual supported subset in [`packages/alienmark/`](../../packages/alienmark/AGENTS.md). When you change supported syntax, update the parser, its tests, and these docs together.
- Contributor docs reference the backend/frontend/architecture — keep them consistent with the code in [`apps/backend/`](../../apps/backend/AGENTS.md) and [`apps/frontend/`](../../apps/frontend/AGENTS.md).

## Verification

```bash
# From docs/<site>/ — strict build matches the CI docs-* jobs
uv run zensical build --strict
uv run zensical build --strict --config-file zensical.zh.toml
```

If the build warns, treat it as a failure — CI runs with `--strict`.
