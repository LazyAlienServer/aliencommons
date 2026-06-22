# AlienCommons

> 每个 TechMC 玩家的共享空间 —— 集发布、讨论、发现于一体的全栈社区平台。

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6-092E20?style=flat-square&logo=django)](https://djangoproject.com)
[![Vue](https://img.shields.io/badge/Vue-3-4FC08D?style=flat-square&logo=vue.js)](https://vuejs.org)
[![Nuxt](https://img.shields.io/badge/Nuxt-4-00DC82?style=flat-square&logo=nuxt.js)](https://nuxt.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

<!-- README-I18N:START -->

[English](./README.md) | **中文**

<!-- README-I18N:END -->

[概述](#概述) • [架构](#架构) • [技术栈](#技术栈) • [快速开始](#快速开始) • [项目结构](#项目结构) • [文档](#文档)

## 概述

AlienCommons 是面向 TechMC Minecraft 服务器的社区平台，集文章发布、话题讨论、书签收藏、点赞评论于一体，配有统一的审核体系。

项目目前仍处于早期阶段，并在密集开发中。

## 架构

```plaintext
┌──────────────────────────────────────────────────────┐
│                      Frontend                        │
│           Nuxt 4 · Vue 3 · Tailwind CSS 4            │
└─────────────────┬────────────────────────────────────┘
                  │ HTTP / WebSocket
┌─────────────────▼────────────────────────────────────┐
│                    Backend API                       │
│           Django 6 · Django REST Framework           │
└──────┬──────────────┬────────────┬───────────────┬───┘
       │              │            │               │
┌──────▼───────┐ ┌────▼────┐ ┌─────▼─────┐ ┌───────▼───────┐
│  PostgreSQL  │ │  Redis  │ │    RQ     │ │   AlienMark   │
│      18      │ │    8    │ │  Workers  │ │   (Fastify)   │
└──────────────┘ └─────────┘ └───────────┘ └───────────────┘
```

## 技术栈

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=py,django,postgres,redis,ts,nuxt,vue,tailwind,docker,grafana" alt="技术栈图标" />
  </a>
</p>

- Python 3.14, Django 6, Django REST Framework, Django Channels, Daphne
- PostgreSQL 18, Redis 8, RQ (`django-tasks-rq`)
- Nuxt 4, Vue 3, TypeScript, Tailwind CSS 4, Pinia
- AlienMark — 自研 TypeScript Markdown 解析器，内部 Fastify 渲染服务
- Grafana, Loki, Grafana Alloy
- Docker Compose, Traefik, AWS, Cloudflare DNS
- pnpm workspaces, Turbo, uv, GitHub Actions

## 快速开始

### 环境要求

- [Docker](https://docs.docker.com/get-docker/) 和 Docker Compose
- [Node.js](https://nodejs.org/) 24+ 和 [pnpm](https://pnpm.io/installation) 11+
- [Python](https://www.python.org/downloads/) 3.14+ 和 [uv](https://docs.astral.sh/uv/)

### 启动项目

```bash
# 克隆仓库并安装依赖
git clone https://github.com/LazyAlienServer/alien-commons.git
cd alien-commons
pnpm install

# 启动完整开发环境
make dev-up
```

这会启动所有服务：PostgreSQL、Redis、后端 API、任务队列、前端开发服务器、AlienMark 以及可观测性栈（Grafana、Loki、Alloy）。

### 运行单个组件

```bash
# 仅启动前端
make frontend-dev          # → http://localhost:8080

# 运行后端测试
make dev-backend-test

# 通过 Turbo 运行所有 Node 检查
make node-check
```

> 更多命令见 `make/docker.mk` 和 `make/node.mk`。

### Node 工具链

Node workspace 使用 pnpm 管理依赖，使用 Turbo 编排跨包任务，并使用 [Vite+](https://viteplus.dev) 执行各包内的格式检查、lint、类型检查、测试以及库/服务构建。

```bash
pnpm run check      # Turbo：先构建依赖，再运行各包检查
pnpm run build      # Turbo：按依赖顺序构建所有 Node 包
pnpm run test       # Turbo：运行 JavaScript 测试
pnpm run typecheck  # Turbo：运行各包类型检查
```

根目录还提供单包便捷脚本，例如 `pnpm run frontend:check`、`pnpm run alienmark:build` 和 `pnpm run alienmark-service:check`。Turbo 会读取 pnpm workspace 依赖图，因此依赖 `alienmark` 的包会先获得它的构建产物。Vite+ 配置位于 [`vite.config.ts`](vite.config.ts)，Turbo 任务规则位于 [`turbo.json`](turbo.json)。

## 项目结构

```
aliencommons/
├── apps/
│   ├── backend/           Django API — 文章、帖子、评论、
│   │                      书签、点赞、举报、任务、用户
│   ├── frontend/          Nuxt 4 前端应用
│   └── alienmark/         内部 Markdown 渲染服务（Fastify）
├── packages/
│   └── alienmark/         TypeScript Markdown 解析器和 HTML 渲染器
├── docs/
│   ├── users/             用户指南（EN / CN）
│   ├── contributors/      开发者文档
│   └── alienmark/         Markdown 引擎文档
├── infra/
│   └── compose/           Docker Compose 配置（dev / stg / pro）
├── o11y/
│   ├── alloy/             Grafana Alloy 日志采集配置
│   ├── grafana/           Grafana 仪表板和配置
│   └── loki/              Loki 日志聚合配置
├── make/                  Docker 和 Node 命令的 Make 目标
└── .github/workflows/     CI/CD 流水线
```

## 文档

| 受众      | 描述                     | 链接                                       |
| --------- | ------------------------ | ------------------------------------------ |
| 用户      | 平台使用指南、社区规范   | [`docs/users/`](docs/users/)               |
| 贡献者    | 架构、环境搭建、开发流程 | [`docs/contributors/`](docs/contributors/) |
| AlienMark | Markdown 语法参考和 API  | [`docs/alienmark/`](docs/alienmark/)       |

所有文档均提供英文和中文版本，使用 [MkDocs](https://www.mkdocs.org/) 和 [Material](https://squidfunk.github.io/mkdocs-material/) 主题构建。

请注意，在当前阶段，部分资料可能尚未完全保持最新。

## 部署环境

AlienCommons 使用三个环境：

- **`dev`** — 本地开发，使用 Docker Compose
- **`stg`** — 预发布环境，托管于 AWS，尽可能与生产环境一致
- **`pro`** — 生产环境，托管于 AWS，使用 Cloudflare DNS 解析 `aliencommons.com`
