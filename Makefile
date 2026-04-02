COMPOSE_BASE = -f infra/compose/docker-compose.base.yml
COMPOSE_DEV = -f infra/compose/docker-compose.dev.yml
COMPOSE_STG = -f infra/compose/docker-compose.stg.yml
COMPOSE_PRO = -f infra/compose/docker-compose.pro.yml
COMPOSE_PROXY = -f infra/compose/docker-compose.proxy.yml

DB = postgres redis
OBSERVE = alloy loki grafana
APP = backend-api backend-task-scheduler backend-task-worker frontend

# DEV
dev-db-up:
	docker compose $(COMPOSE_BASE) $(COMPOSE_DEV) up $(DB)
dev-observe-up:
	docker compose $(COMPOSE_BASE) $(COMPOSE_DEV) up $(OBSERVE)
dev-up:
	docker compose $(COMPOSE_BASE) $(COMPOSE_DEV) up -d $(DB)
	docker compose $(COMPOSE_BASE) $(COMPOSE_DEV) run --rm backend-init
	docker compose $(COMPOSE_BASE) $(COMPOSE_DEV) up -d $(OBSERVE)
	docker compose $(COMPOSE_BASE) $(COMPOSE_DEV) up --build $(APP)
dev-down:
	docker compose $(COMPOSE_BASE) $(COMPOSE_DEV) down
dev-down-v:
	docker compose $(COMPOSE_BASE) $(COMPOSE_DEV) down -v

# STG
stg-up:
	docker compose $(COMPOSE_BASE) $(COMPOSE_STG) up -d $(DB)
	docker compose $(COMPOSE_BASE) $(COMPOSE_STG) run --rm backend-init
	docker compose $(COMPOSE_BASE) $(COMPOSE_STG) up -d $(OBSERVE)
	docker compose $(COMPOSE_BASE) $(COMPOSE_STG) up -d --build $(APP)
stg-down:
	docker compose $(COMPOSE_BASE) $(COMPOSE_STG) down
stg-down-v:
	docker compose $(COMPOSE_BASE) $(COMPOSE_STG) down -v
stg-backend-api-bash:
	docker compose $(COMPOSE_BASE) $(COMPOSE_STG) exec backend-api bash
stg-backend-api-log:
	docker compose $(COMPOSE_BASE) $(COMPOSE_STG) logs backend-api
stg-frontend-log:
	docker compose $(COMPOSE_BASE) $(COMPOSE_STG) logs frontend

# PRO
pro-up:
	docker compose $(COMPOSE_BASE) $(COMPOSE_PRO) up -d $(DB)
	docker compose $(COMPOSE_BASE) $(COMPOSE_PRO) run --rm backend-init
	docker compose $(COMPOSE_BASE) $(COMPOSE_PRO) up -d $(OBSERVE)
	docker compose $(COMPOSE_BASE) $(COMPOSE_PRO) up -d --build $(APP)
pro-down:
	docker compose $(COMPOSE_BASE) $(COMPOSE_PRO) down
pro-backend-api-bash:
	docker compose $(COMPOSE_BASE) $(COMPOSE_PRO) exec backend-api bash
pro-backend-api-log:
	docker compose $(COMPOSE_BASE) $(COMPOSE_PRO) logs backend-api
pro-frontend-log:
	docker compose $(COMPOSE_BASE) $(COMPOSE_PRO) logs frontend

# PROXY
proxy-up:
	docker compose $(COMPOSE_PROXY) up -d
proxy-down:
	docker compose $(COMPOSE_PROXY) down
proxy-log:
	docker compose $(COMPOSE_PROXY) logs traefik