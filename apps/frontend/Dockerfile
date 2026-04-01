FROM node:23 AS build-stage

ENV NODE_OPTIONS="--max-old-space-size=512"

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_MODE=production
RUN npm run build -- --mode ${VITE_MODE}

FROM nginx:1.27.4-alpine AS production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
