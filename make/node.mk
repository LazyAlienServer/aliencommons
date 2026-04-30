PNPM = pnpm
PNPM_FRONTEND = $(PNPM) --filter frontend
PNPM_ALIENMARK = $(PNPM) --filter alienmark
PNPM_ALIENMARK_SERVICE = $(PNPM) --filter alienmark-service

.PHONY: node-install node-build node-test node-check frontend-dev frontend-build frontend-preview alienmark-dev alienmark-build alienmark-test alienmark-check alienmark-service-dev alienmark-service-build alienmark-service-start alienmark-service-check

# NODE WORKSPACE
node-install:
	$(PNPM) install

node-build:
	$(PNPM) -r --if-present build

node-test:
	$(PNPM) -r --if-present test

node-check:
	$(PNPM) -r --if-present check

frontend-dev:
	$(PNPM_FRONTEND) dev

frontend-build:
	$(PNPM_FRONTEND) build

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

alienmark-service-dev:
	$(PNPM_ALIENMARK_SERVICE) dev

alienmark-service-build:
	$(PNPM_ALIENMARK_SERVICE) build

alienmark-service-start:
	$(PNPM_ALIENMARK_SERVICE) start

alienmark-service-check:
	$(PNPM_ALIENMARK_SERVICE) check
