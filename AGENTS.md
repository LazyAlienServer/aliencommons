# Agent Guide

Keep changes small, intentional, and consistent with the existing project.

## Project Shape

This is a monorepo. The main areas are:

- `apps/` for deployable applications.
- `packages/` for reusable packages.
- `docs/` for documentation.
- `infra/`, `o11y/`, and `make/` for operations and tooling.

Prefer the conventions already present in the area you are editing.

## Working Rules

- Read the nearby code before changing it.
- Do not rewrite unrelated files or reformat broad areas without a reason.
- Do not remove or revert user changes unless explicitly asked.
- Keep secrets, credentials, and local environment files out of commits.
- Use existing scripts, Make targets, and package commands when available.
- Add or update tests when the change affects behavior.

## Verification

Run the smallest relevant checks for the change. If a check cannot be run, mention that in the final response.

## Git

- Use focused commits and clear commit messages.
- Feature work should normally branch from the active development branch.
- Production releases should be represented by tags, not by editing this file.
