# AlienCommons

> The common planet for all Minecraft players — a community platform for publishing, discussion, and discovery.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6-092E20?style=flat-square&logo=django)](https://djangoproject.com)
[![Vue](https://img.shields.io/badge/Vue-3-4FC08D?style=flat-square&logo=vue.js)](https://vuejs.org)
[![Nuxt](https://img.shields.io/badge/Nuxt-4-00DC82?style=flat-square&logo=nuxt.js)](https://nuxt.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

<!-- README-I18N:START -->

**English** | [中文](./README.zh.md)

<!-- README-I18N:END -->

[Overview](#overview) • [Architecture](#architecture) • [Tech Stack](#tech-stack) • [Getting Started](#getting-started) • [Project Structure](#project-structure) • [Documentation](#documentation)

## Overview

AlienCommons is a community platform built for Technical Minecraft players. It provides a space for players to publish articles and participate in discussions.

The project is currently in its early stages under heavy development.

## Architecture

```plaintext
┌──────────────────────────────────────────────────────┐
│                       Frontend                       │
│           Nuxt 4 · Vue 3 · Tailwind CSS 4            │
└─────────────────┬────────────────────────────────────┘
                  │ HTTP / WebSocket
┌─────────────────▼────────────────────────────────────┐
│                     Backend API                      │
│           Django 6 · Django REST Framework           │
└──────┬──────────────┬────────────┬───────────────┬───┘
       │              │            │               │
┌──────▼───────┐ ┌────▼────┐ ┌─────▼─────┐ ┌───────▼───────┐
│  PostgreSQL  │ │  Redis  │ │    RQ     │ │   AlienMark   │
│      18      │ │    8    │ │  Workers  │ │   (Fastify)   │
└──────────────┘ └─────────┘ └───────────┘ └───────────────┘
```

## Tech Stack

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=py,django,postgres,redis,ts,nuxt,vue,tailwind,docker,grafana" alt="Tech stack icons" />
  </a>
</p>

- Python 3.14, Django 6, Django REST Framework, Django Channels, Daphne
- PostgreSQL 18, Redis 8, RQ (`django-tasks-rq`)
- Nuxt 4, Vue 3, TypeScript, Tailwind CSS 4, Pinia
- AlienMark — custom TypeScript Markdown parser, internal Fastify rendering service
- Grafana, Loki, Grafana Alloy
- Docker Compose, Traefik, AWS, Cloudflare DNS
- pnpm workspaces, Turbo, uv, GitHub Actions

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Node.js](https://nodejs.org/) 24+ and [pnpm](https://pnpm.io/installation) 11+
- [Python](https://www.python.org/downloads/) 3.14+ and [uv](https://docs.astral.sh/uv/)

### Quick Start

```bash
# Clone and install dependencies
git clone https://github.com/LazyAlienServer/aliencommons.git
cd aliencommons
pnpm install

# Start the full development stack
make dev-up
```

This launches all services: PostgreSQL, Redis, the backend API, task workers, the frontend dev server, AlienMark, and the observability stack (Grafana, Loki, Alloy).

### Running Individual Components

```bash
# Frontend only
make frontend-dev          # → http://localhost:8080

# Backend tests
make dev-backend-test

# Run all Node checks through Turbo
make node-check
```

> For the full set of available commands, see `make/docker.mk` and `make/node.mk`.

### Node Tooling

The Node workspace uses pnpm for dependency management, Turbo for cross-package task orchestration, and [Vite+](https://viteplus.dev) for package-level formatting, linting, type checks, tests, and library/service builds.

```bash
pnpm run check      # Turbo: build dependencies, then run package checks
pnpm run build      # Turbo: build all Node packages in dependency order
pnpm run test       # Turbo: run JavaScript tests
pnpm run typecheck  # Turbo: run package type checks
pnpm run knip       # Advisory unused-code and unused-dependency report
```

Single-package convenience scripts are available from the root, such as `pnpm run frontend:check`, `pnpm run alienmark:build`, and `pnpm run alienmark-service:check`. Turbo uses the pnpm workspace graph so packages depending on `alienmark` get its build first. Vite+ configuration lives in [`vite.config.ts`](vite.config.ts), Turbo task rules live in [`turbo.json`](turbo.json), and Knip advisory rules live in [`knip.jsonc`](knip.jsonc). Knip is intentionally separate from `pnpm run check`; use `pnpm run knip:strict` only when you want unused-code findings to produce a non-zero exit code.

## Project Structure

```
aliencommons/
├── apps/
│   ├── backend/          Django API — articles, posts, comments,
│   │                     bookmarks, reactions, reports, tasks, users
│   ├── frontend/         Nuxt 4 frontend application
│   └── alienmark/        Internal Markdown rendering service (Fastify)
├── packages/
│   └── alienmark/        TypeScript Markdown parser and HTML renderer
├── docs/
│   ├── users/            User guide (EN / CN)
│   ├── contributors/     Developer documentation
│   └── alienmark/        Markdown engine documentation
├── infra/
│   └── compose/          Docker Compose configurations (dev / stg / pro)
├── o11y/
│   ├── alloy/            Grafana Alloy log collection configs
│   ├── grafana/          Grafana dashboards and provisioning
│   └── loki/             Loki log aggregation configs
├── make/                 Make targets for Docker and Node commands
└── .github/workflows/    CI/CD pipelines
```

## Documentation

| Audience     | Description                               | Link                                       |
| ------------ | ----------------------------------------- | ------------------------------------------ |
| Users        | Platform usage guide, community rules     | [`docs/users/`](docs/users/)               |
| Contributors | Architecture, setup, development workflow | [`docs/contributors/`](docs/contributors/) |
| AlienMark    | Markdown syntax reference and API         | [`docs/alienmark/`](docs/alienmark/)       |

All documentation is available in English and Chinese (中文) and built with [MkDocs](https://www.mkdocs.org/) using the [Material](https://squidfunk.github.io/mkdocs-material/) theme.

Please note that some materials may be not fully up-to-date in this stage.

## Environments

AlienCommons uses three environments:

- **`dev`** — local development with Docker Compose
- **`stg`** — staging, hosted on AWS, mirrors production as closely as practical
- **`pro`** — production, hosted on AWS with Cloudflare DNS for `aliencommons.com`
