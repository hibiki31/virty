# ビルド環境
FROM node:24-bullseye as build-stage
WORKDIR /app

RUN corepack enable
COPY package.json ./
COPY pnpm-lock.yaml ./

RUN pnpm install

COPY . .
RUN pnpm build

# 本番環境
FROM nginx:stable-alpine as production-stage
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]