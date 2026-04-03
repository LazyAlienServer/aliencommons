# AlienCommons

A website for every Technical Minecraft player.

## Tech Stacks

This is a 'monorepo-based' web project with frontend-backend separation architecture.  

Frontend: **Vue3 + Vite**  
Backend: **Django + Django Rest Framework**  
Database: **PostgreSQL**  
Cache: **Redis**  
Documentation: **MkDocs**  
Observability: **Grafana + Loki + Alloy**  
Proxy: **Treafik**  
Deployment: **Docker**

[![My Skills](https://skillicons.dev/icons?i=py,html,css,tailwind,ts,js,vue,postgres,redis,docker)](https://skillicons.dev)

## Structure
`app/`: Web Applications
- **Django** backend
- **Vue** frontend

`infra/`: Infrastructure
- docker compose files
- environment files

`o11y/`: Observability
- **grafana** config files
- **loki** config files
- **alloy** config files

`docs/`: Developer Documentation  
- **mkdocs**

`.github/`: GitHub Configs
- **GitHub** Workflows

`Makefile`: Command Shortcuts

## Developer Documentation

> [!Important]
> This documentation is not yet up-to-date.

Developer Documentation: [AlienCommons Docs](https://lazyalienserver.github.io/alien-commons/)