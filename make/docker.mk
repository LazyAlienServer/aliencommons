COMPOSE_BASE = -f infra/compose/docker-compose.base.yml
COMPOSE_DEV = -f infra/compose/docker-compose.dev.yml
COMPOSE_STG = -f infra/compose/docker-compose.stg.yml
COMPOSE_PRO = -f infra/compose/docker-compose.pro.yml
COMPOSE_PROXY = -f infra/compose/docker-compose.proxy.yml

DEV_COMPOSE = docker compose $(COMPOSE_BASE) $(COMPOSE_DEV)
STG_COMPOSE = docker compose $(COMPOSE_BASE) $(COMPOSE_STG)
PRO_COMPOSE = docker compose $(COMPOSE_BASE) $(COMPOSE_PRO)
PROXY_COMPOSE = docker compose $(COMPOSE_PROXY)

DEV_MANAGE = $(DEV_COMPOSE) run --rm backend-api python manage.py
DEV_MANAGE_NO_DEPS = $(DEV_COMPOSE) run --rm --no-deps backend-api python manage.py
DEV_MANAGE_TEST = $(DEV_COMPOSE) run --rm --no-deps -e DJANGO_SETTINGS_MODULE=backend.settings.test backend-api python manage.py

DB = postgres redis
OBSERVE = alloy loki grafana
APP = backend-api backend-task-scheduler backend-task-worker frontend alienmark

.PHONY: dev-db-up dev-observe-up dev-up dev-down dev-down-v \
	dev-backend-bash dev-backend-shell dev-backend-runserver \
	dev-backend-makemigrations dev-backend-migrate dev-backend-createsuperuser \
	dev-backend-test dev-backend-check dev-backend-apidoc \
	dev-backend-init-tasks dev-backend-runscheduler dev-backend-runrqworker \
	stg-up stg-down stg-down-v stg-backend-api-bash stg-backend-api-log stg-frontend-log \
	pro-up pro-down pro-backend-api-bash pro-backend-api-log pro-frontend-log \
	proxy-up proxy-down proxy-log

# DEVELOPMENT
dev-db-up:
	$(DEV_COMPOSE) up $(DB)

dev-observe-up:
	$(DEV_COMPOSE) up $(OBSERVE)

dev-up:
	$(DEV_COMPOSE) up -d $(DB)
	$(DEV_COMPOSE) run --rm backend-init
	$(DEV_COMPOSE) up -d $(OBSERVE)
	$(DEV_COMPOSE) up --build $(APP)

dev-down:
	$(DEV_COMPOSE) down

dev-down-v:
	$(DEV_COMPOSE) down -v

dev-backend-bash:
	$(DEV_COMPOSE) run --rm backend-api bash

dev-backend-shell:
	$(DEV_MANAGE) shell

dev-backend-runserver:
	$(DEV_COMPOSE) run --rm --service-ports backend-api python manage.py runserver 0.0.0.0:8000

dev-backend-makemigrations:
	$(DEV_MANAGE_NO_DEPS) makemigrations

dev-backend-migrate:
	$(DEV_MANAGE) migrate

dev-backend-createsuperuser:
	$(DEV_MANAGE) createsuperuser

dev-backend-test:
	$(DEV_MANAGE_TEST) test

dev-backend-check:
	$(DEV_MANAGE_NO_DEPS) check

dev-backend-apidoc:
	$(DEV_COMPOSE) run --rm --no-deps -e DJANGO_SETTINGS_MODULE=backend.settings.test backend-api python manage.py spectacular --file openapi.yaml --validate

dev-backend-init-tasks:
	$(DEV_MANAGE) init_tasks

dev-backend-runscheduler:
	$(DEV_MANAGE) runscheduler

dev-backend-runrqworker:
	$(DEV_MANAGE) rqworker default email maintenance

# STAGING
stg-up:
	$(STG_COMPOSE) up -d $(DB)
	$(STG_COMPOSE) run --rm backend-init
	$(STG_COMPOSE) up -d $(OBSERVE)
	$(STG_COMPOSE) up -d --build $(APP)

stg-down:
	$(STG_COMPOSE) down

stg-down-v:
	$(STG_COMPOSE) down -v

stg-backend-api-bash:
	$(STG_COMPOSE) exec backend-api bash

stg-backend-api-log:
	$(STG_COMPOSE) logs backend-api

stg-frontend-log:
	$(STG_COMPOSE) logs frontend

# PRODUCTION
pro-up:
	$(PRO_COMPOSE) up -d $(DB)
	$(PRO_COMPOSE) run --rm backend-init
	$(PRO_COMPOSE) up -d $(OBSERVE)
	$(PRO_COMPOSE) up -d --build $(APP)

pro-down:
	$(PRO_COMPOSE) down

pro-backend-api-bash:
	$(PRO_COMPOSE) exec backend-api bash

pro-backend-api-log:
	$(PRO_COMPOSE) logs backend-api

pro-frontend-log:
	$(PRO_COMPOSE) logs frontend

# PROXY
proxy-up:
	$(PROXY_COMPOSE) up -d

proxy-down:
	$(PROXY_COMPOSE) down

proxy-log:
	$(PROXY_COMPOSE) logs traefik
