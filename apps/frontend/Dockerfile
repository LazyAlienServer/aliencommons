ARG NODE_IMAGE=node:24-slim

FROM ${NODE_IMAGE} AS deps

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /workspace

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/frontend/package.json apps/frontend/package.json
COPY packages/alienmark/package.json packages/alienmark/package.json

RUN pnpm install --frozen-lockfile --filter aliencommons --filter frontend... --ignore-scripts

FROM deps AS build

COPY turbo.json vite.config.ts ./
COPY apps/frontend apps/frontend
COPY packages/alienmark packages/alienmark

RUN pnpm turbo run build --filter=frontend

FROM ${NODE_IMAGE} AS runtime

ENV NODE_ENV=production
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=3000

WORKDIR /app

COPY --from=build --chown=node:node /workspace/apps/frontend/.output .output

USER node

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
