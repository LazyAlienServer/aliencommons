# Documentation Agent Guide

These rules apply to documentation under `docs/`.

## Scope

Each subdirectory is a separate documentation project. Prefer shared guidance here, and add a more specific `AGENTS.md` inside a subproject only when that project needs its own rules.

## Writing

- Keep documentation clear, practical, and close to the current project behavior.
- Prefer small, focused edits over broad rewrites.
- Preserve the existing page structure, heading style, and terminology.
- Do not invent features, commands, or deployment steps that are not present in the project.

## Languages

- When a page exists in both English and Chinese, update both versions together.
- Keep the English and Chinese pages equivalent in meaning, even if the wording is not literal.
- If only one language exists for a page, follow the existing structure and do not create a second language unless the task asks for it.

## MkDocs

- Keep `mkdocs.yml` navigation in sync with added, moved, or removed pages.
- Use existing MkDocs and Material conventions already present in the subproject.
- Do not commit generated site output unless the task explicitly asks for it.

## Verification

Run the smallest relevant documentation build or check when practical. If it is not run, mention that in the final response.
