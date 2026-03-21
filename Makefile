dev:
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml up
dev-down:
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml down
dev-downv:
	docker compose -f docker-compose.base.yml -f docker-compose dev.yml down -v

devfull:
	docker compose -f docker-compose.base.yml -f docker-compose.full-dev.yml up --build
pro:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml up -d --build
staging:
	docker compose -f docker-compose.base.yml -f docker-compose.staging.yml up -d --build
traefik:
	docker compose -f docker-compose.traefik.yml up -d

devfull-down:
	docker compose -f docker-compose.base.yml -f docker-compose.full-dev.yml down
pro-down:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml down
staging-down:
	docker compose -f docker-compose.base.yml -f docker-compose.staging.yml down
traefik-down:
	docker compose -f docker-compose.traefik.yml down

devfull-downv:
	docker compose -f docker-compose.base.yml -f docker-compose.full-dev.yml down -v
staging-downv:
	docker compose -f docker-compose.base.yml -f docker-compose.staging.yml down -v

devfull-backendbash:
	docker compose -f docker-compose.base.yml -f docker-compose.full-dev.yml exec backend bash
pro-backendbash:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml exec backend bash
staging-backendbash:
	docker compose -f docker-compose.base.yml -f docker-compose.staging.yml exec backend bash

pro-backendlog:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml logs backend
pro-frontendlog:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml logs frontend
staging-backendlog:
	docker compose -f docker-compose.base.yml -f docker-compose.staging.yml logs backend
staging-frontendlog:
	docker compose -f docker-compose.base.yml -f docker-compose.staging.yml logs frontend
traefik-log:
	docker compose -f docker-compose.traefik.yml logs traefik

apidoc:
	python manage.py spectacular --file openapi.yaml
