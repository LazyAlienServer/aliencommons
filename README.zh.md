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

项目尚处早期，后端已可投入生产，前端仍在开发中。

## 架构

```plaintext
┌──────────────────────────────────────────────────────┐
│                      Frontend                        │
│           Nuxt 4 · Vue 3 · Tailwind CSS 4            │
│             (Server-Side Rendered SPA)               │
└─────────────────┬────────────────────────────────────┘
                  │ HTTP / WebSocket
┌─────────────────▼────────────────────────────────────┐
│                    Backend API                       │
│           Django 6 · Django REST Framework           │
│            Django Channels · Daphne (ASGI)           │
└────┬────────────┬────────────┬───────────────┬───────┘
     │            │            │               │
┌────▼─────┐ ┌────▼────┐ ┌─────▼─────┐ ┌───────▼───────┐
│PostgreSQL│ │  Redis  │ │    RQ     │ │   AlienMark   │
│    18    │ │    8    │ │  Workers  │ │   (Fastify)   │
└──────────┘ └─────────┘ └───────────┘ └───────────────┘
```

后端调用内部 **AlienMark** 服务（Fastify）完成服务端 Markdown 转 HTML 渲染。实时通信由 Django Channels 通过 WebSocket 承载。后台任务（邮件、维护）由 RQ 任务队列处理，依赖 Redis 作为消息代理。

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

# 运行所有 Node 检查（lint、类型检查、代码风格）
make node-check
```

> 更多命令见 `make/docker.mk` 和 `make/node.mk`。

### Vite+

前端工具链统一使用 [Vite+](https://viteplus.dev) — 一个 `vp` CLI 可以替代 pnpm、Vite、Vitest 和代码检查命令：

```bash
vp dev          # 启动前端开发服务器
vp check        # 格式化、代码检查和类型检查
vp test         # 运行 JavaScript 测试
vp build        # 构建前端生产版本
```

完整命令列表参见 [Vite+ 指南](https://viteplus.dev/guide/)。项目配置位于 [`vite.config.ts`](vite.config.ts)。

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
│   ├── users/             用户指南（EN / 中文）
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

## 部署环境

AlienCommons 使用三个环境：

- **`dev`** — 本地开发，使用 Docker Compose
- **`stg`** — 预发布环境，托管于 AWS，尽可能与生产环境一致
- **`pro`** — 生产环境，托管于 AWS，使用 Cloudflare DNS 解析 `aliencommons.com`
