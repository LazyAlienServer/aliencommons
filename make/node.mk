PNPM = pnpm

.PHONY: node-install node-build node-test node-check node-typecheck node-lint node-fmt node-knip frontend-dev frontend-build frontend-check frontend-typecheck frontend-preview alienmark-dev alienmark-build alienmark-test alienmark-check alienmark-typecheck alienmark-service-dev alienmark-service-build alienmark-service-start alienmark-service-check alienmark-service-typecheck

# NODE WORKSPACE
node-install:
	$(PNPM) install

node-build:
	$(PNPM) run build

node-test:
	$(PNPM) run test

node-check:
	$(PNPM) run check

node-typecheck:
	$(PNPM) run typecheck

node-lint:
	$(PNPM) run lint:check

node-fmt:
	$(PNPM) run fmt:check

node-knip:
	$(PNPM) run knip

frontend-dev:
	$(PNPM) --filter frontend dev

frontend-build:
	$(PNPM) turbo run build --filter=frontend

frontend-check:
	$(PNPM) turbo run check --filter=frontend

frontend-typecheck:
	$(PNPM) turbo run typecheck --filter=frontend

frontend-preview:
	$(PNPM) --filter frontend preview

alienmark-dev:
	$(PNPM) --filter alienmark dev

alienmark-build:
	$(PNPM) turbo run build --filter=alienmark

alienmark-test:
	$(PNPM) turbo run test --filter=alienmark

alienmark-check:
	$(PNPM) turbo run check --filter=alienmark

alienmark-typecheck:
	$(PNPM) turbo run typecheck --filter=alienmark

alienmark-service-dev:
	$(PNPM) --filter alienmark-service dev

alienmark-service-build:
	$(PNPM) turbo run build --filter=alienmark-service

alienmark-service-start:
	$(PNPM) --filter alienmark-service start

alienmark-service-check:
	$(PNPM) turbo run check --filter=alienmark-service

alienmark-service-typecheck:
	$(PNPM) turbo run typecheck --filter=alienmark-service
