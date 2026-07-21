ARG NODE_IMAGE=node:24-slim

FROM ${NODE_IMAGE} AS deps

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /workspace

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/frontend/package.json apps/frontend/package.json

RUN pnpm install --frozen-lockfile --filter frontend --ignore-scripts

FROM deps AS build

COPY apps/frontend apps/frontend

RUN pnpm --filter frontend build

FROM ${NODE_IMAGE} AS runtime

ENV NODE_ENV=production
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=3000

WORKDIR /app

COPY --from=build --chown=node:node /workspace/apps/frontend/.output .output

USER node

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
