PNPM = pnpm
PNPM_FRONTEND = $(PNPM) --filter frontend
PNPM_ALIENMARK = $(PNPM) --filter alienmark
PNPM_ALIENMARK_SERVICE = $(PNPM) --filter alienmark-service

.PHONY: node-install node-build node-test node-check node-typecheck node-lint node-style frontend-dev frontend-build frontend-check frontend-typecheck frontend-preview alienmark-dev alienmark-build alienmark-test alienmark-check alienmark-typecheck alienmark-service-dev alienmark-service-build alienmark-service-start alienmark-service-check alienmark-service-typecheck

# NODE WORKSPACE
node-install:
	$(PNPM) install

node-build:
	$(PNPM) -r --if-present build

node-test:
	$(PNPM) -r --if-present test

node-check:
	$(PNPM) run node:check

node-typecheck:
	$(PNPM) run node:typecheck

node-lint:
	$(PNPM) run lint:check

node-style:
	$(PNPM) run style:check

frontend-dev:
	$(PNPM_FRONTEND) dev

frontend-build:
	$(PNPM_FRONTEND) build

frontend-check:
	$(PNPM_FRONTEND) check

frontend-typecheck:
	$(PNPM_FRONTEND) typecheck

frontend-preview:
	$(PNPM_FRONTEND) preview

alienmark-dev:
	$(PNPM_ALIENMARK) dev

alienmark-build:
	$(PNPM_ALIENMARK) build

alienmark-test:
	$(PNPM_ALIENMARK) test

alienmark-check:
	$(PNPM_ALIENMARK) check

alienmark-typecheck:
	$(PNPM_ALIENMARK) typecheck

alienmark-service-dev:
	$(PNPM_ALIENMARK_SERVICE) dev

alienmark-service-build:
	$(PNPM_ALIENMARK_SERVICE) build

alienmark-service-start:
	$(PNPM_ALIENMARK_SERVICE) start

alienmark-service-check:
	$(PNPM_ALIENMARK) build
	$(PNPM_ALIENMARK_SERVICE) check

alienmark-service-typecheck:
	$(PNPM_ALIENMARK) build
	$(PNPM_ALIENMARK_SERVICE) typecheck
