COMPOSE_BASE = -f infra/compose/docker-compose.base.yml
COMPOSE_DEV = -f infra/compose/docker-compose.dev.yml
COMPOSE_STG = -f infra/compose/docker-compose.stg.yml
COMPOSE_PRO = -f infra/compose/docker-compose.pro.yml
COMPOSE_PROXY = -f infra/compose/docker-compose.proxy.yml

DEV_COMPOSE = docker compose $(COMPOSE_BASE) $(COMPOSE_DEV)
DEV_MANAGE = $(DEV_COMPOSE) run --rm backend-api python manage.py
DEV_MANAGE_NO_DEPS = $(DEV_COMPOSE) run --rm --no-deps backend-api python manage.py
DEV_MANAGE_TEST = $(DEV_COMPOSE) run --rm --no-deps -e DJANGO_SETTINGS_MODULE=backend.settings.test backend-api python manage.py

DB = postgres redis
OBSERVE = alloy loki grafana
APP = backend-api backend-task-scheduler backend-task-worker frontend

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

# PRODUCTION
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
