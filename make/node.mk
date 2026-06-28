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
	$(PNPM) run frontend:dev

frontend-build:
	$(PNPM) run frontend:build

frontend-check:
	$(PNPM) run frontend:check

frontend-typecheck:
	$(PNPM) run frontend:typecheck

frontend-preview:
	$(PNPM) run frontend:preview

alienmark-dev:
	$(PNPM) run alienmark:dev

alienmark-build:
	$(PNPM) run alienmark:build

alienmark-test:
	$(PNPM) run alienmark:test

alienmark-check:
	$(PNPM) run alienmark:check

alienmark-typecheck:
	$(PNPM) run alienmark:typecheck

alienmark-service-dev:
	$(PNPM) run alienmark-service:dev

alienmark-service-build:
	$(PNPM) run alienmark-service:build

alienmark-service-start:
	$(PNPM) run alienmark-service:start

alienmark-service-check:
	$(PNPM) run alienmark-service:check

alienmark-service-typecheck:
	$(PNPM) run alienmark-service:typecheck
