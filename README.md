# AlienCommons

> The common land for every TechMC player — a full-stack community platform for publishing, discussion, and discovery.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6-092E20?style=flat-square&logo=django)](https://djangoproject.com)
[![Vue](https://img.shields.io/badge/Vue-3-4FC08D?style=flat-square&logo=vue.js)](https://vuejs.org)
[![Nuxt](https://img.shields.io/badge/Nuxt-4-00DC82?style=flat-square&logo=nuxt.js)](https://nuxt.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

[Overview](#overview) • [Architecture](#architecture) • [Tech Stack](#tech-stack) • [Getting Started](#getting-started) • [Project Structure](#project-structure) • [Documentation](#documentation)

## Overview

AlienCommons is a community platform built for the TechMC Minecraft server. It provides a space for players to publish articles, participate in discussions, manage bookmarks, and engage with content through reactions and comments — all under a unified moderation system.

The project is currently in its early stages, with a production-ready backend and a modern frontend under active development.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                       Frontend                       │
│           Nuxt 4 · Vue 3 · Tailwind CSS 4            │
│             (Server-Side Rendered SPA)               │
└─────────────────┬────────────────────────────────────┘
                  │ HTTP / WebSocket
┌─────────────────▼────────────────────────────────────┐
│                     Backend API                      │
│           Django 6 · Django REST Framework           │
│            Django Channels · Daphne (ASGI)           │
└────┬────────────┬────────────┬───────────────┬───────┘
     │            │            │               │
┌────▼─────┐ ┌────▼────┐ ┌─────▼─────┐ ┌───────▼───────┐
│PostgreSQL│ │  Redis  │ │    RQ     │ │   AlienMark   │
│    18    │ │    8    │ │  Workers  │ │   (Fastify)   │
└──────────┘ └─────────┘ └───────────┘ └───────────────┘
```

The backend communicates with an internal **AlienMark** service (Fastify) for server-side Markdown-to-HTML rendering. Real-time features are powered by Django Channels over WebSockets. Background processing (email, maintenance) runs through RQ task workers backed by Redis.

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.14, Django 6, Django REST Framework, Django Channels |
| **Database** | PostgreSQL 18 |
| **Cache / Queue** | Redis 8, RQ (via django-tasks-rq) |
| **Frontend** | Nuxt 4, Vue 3, TypeScript, Tailwind CSS 4, Pinia |
| **Markdown** | AlienMark (custom TypeScript parser + Fastify HTTP service) |
| **Observability** | Grafana, Loki, Grafana Alloy |
| **Infrastructure** | Docker Compose, Traefik, AWS, Cloudflare DNS |
| **Package Management** | pnpm (Node), uv (Python) |
| **Monorepo** | pnpm workspaces, Turbo |
| **CI/CD** | GitHub Actions |
| **Documentation** | MkDocs + Material for MkDocs (English / 中文) |

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Node.js](https://nodejs.org/) 24+ and [pnpm](https://pnpm.io/installation) 11+
- [Python](https://www.python.org/downloads/) 3.14+ and [uv](https://docs.astral.sh/uv/)

### Quick Start

```bash
# Clone and install dependencies
git clone https://github.com/LazyAlienServer/alien-commons.git
cd alien-commons
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

# Run all Node checks (lint, typecheck, style)
make node-check
```

> For the full set of available commands, see `make/docker.mk` and `make/node.mk`.

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
│   ├── users/            User guide (EN / 中文)
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

| Audience | Description | Link |
|---|---|---|
| Users | Platform usage guide, community rules | [`docs/users/`](docs/users/) |
| Contributors | Architecture, setup, development workflow | [`docs/contributors/`](docs/contributors/) |
| AlienMark | Markdown syntax reference and API | [`docs/alienmark/`](docs/alienmark/) |

All documentation is available in English and Chinese (中文) and built with [MkDocs](https://www.mkdocs.org/) using the [Material](https://squidfunk.github.io/mkdocs-material/) theme.

## Environments

AlienCommons uses three environments:

- **`dev`** — local development with Docker Compose
- **`stg`** — staging, hosted on AWS, mirrors production as closely as practical
- **`pro`** — production, hosted on AWS with Cloudflare DNS for `aliencommons.com`
