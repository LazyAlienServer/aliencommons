ARG NODE_IMAGE=node:24-slim

FROM ${NODE_IMAGE} AS deps

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /workspace

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/alienmark/package.json apps/alienmark/package.json
COPY packages/alienmark/package.json packages/alienmark/package.json

RUN pnpm install --frozen-lockfile

FROM deps AS build

COPY apps/alienmark apps/alienmark
COPY packages/alienmark packages/alienmark

RUN pnpm --filter alienmark build
RUN pnpm --filter alienmark-service build

FROM ${NODE_IMAGE} AS runtime

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8787

WORKDIR /workspace

COPY --from=build /workspace/package.json /workspace/pnpm-lock.yaml /workspace/pnpm-workspace.yaml ./
COPY --from=build /workspace/node_modules ./node_modules
COPY --from=build /workspace/apps/alienmark/package.json apps/alienmark/package.json
COPY --from=build /workspace/apps/alienmark/node_modules apps/alienmark/node_modules
COPY --from=build /workspace/apps/alienmark/dist apps/alienmark/dist
COPY --from=build /workspace/packages/alienmark/package.json packages/alienmark/package.json
COPY --from=build /workspace/packages/alienmark/dist packages/alienmark/dist

EXPOSE 8787

CMD ["node", "apps/alienmark/dist/server.mjs"]
