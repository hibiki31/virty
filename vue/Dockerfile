# ビルド環境
FROM node:24-bullseye AS build-stage
WORKDIR /app

RUN corepack enable
COPY package.json ./
COPY pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

COPY . .
RUN CHOKIDAR_USEPOLLING=true pnpm build

# 本番環境
FROM nginx:stable-alpine AS production-stage
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
