devdb:
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml up postgres redis
dev:
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml up
dev-down:
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml down
dev-downv:
	docker compose -f docker-compose.base.yml -f docker-compose dev.yml down -v

devfull:
	docker compose -f docker-compose.base.yml -f docker-compose.fulldev.yml up --build
pro:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml up -d --build
stg:
	docker compose -f docker-compose.base.yml -f docker-compose.stg.yml up -d --build
traefik:
	docker compose -f docker-compose.traefik.yml up -d

devfull-down:
	docker compose -f docker-compose.base.yml -f docker-compose.fulldev.yml down
pro-down:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml down
stg-down:
	docker compose -f docker-compose.base.yml -f docker-compose.stg.yml down
traefik-down:
	docker compose -f docker-compose.traefik.yml down

devfull-downv:
	docker compose -f docker-compose.base.yml -f docker-compose.fulldev.yml down -v
stg-downv:
	docker compose -f docker-compose.base.yml -f docker-compose.stg.yml down -v

devfull-backendbash:
	docker compose -f docker-compose.base.yml -f docker-compose.fulldev.yml exec backend bash
pro-backendbash:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml exec backend bash
stg-backendbash:
	docker compose -f docker-compose.base.yml -f docker-compose.stg.yml exec backend bash

pro-backendlog:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml logs backend
pro-frontendlog:
	docker compose -f docker-compose.base.yml -f docker-compose.pro.yml logs frontend
stg-backendlog:
	docker compose -f docker-compose.base.yml -f docker-compose.stg.yml logs backend
stg-frontendlog:
	docker compose -f docker-compose.base.yml -f docker-compose.stg.yml logs frontend
traefik-log:
	docker compose -f docker-compose.traefik.yml logs traefik