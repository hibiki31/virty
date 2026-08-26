# 開発・依存関係環境
FROM node:24-bullseye@sha256:e98b72e72be9ca56f9467559af60619f738b736c0622b7a9afa39d8fc6fed2b5 AS development
WORKDIR /workspace/vue

RUN corepack enable \
    && mkdir -p /tmp/virty-web-home \
    && chmod 0777 /tmp/virty-web-home \
    && chown node:node /workspace/vue
USER node

COPY --chown=node:node package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile \
    && mkdir -p node_modules/.tmp \
    && chmod 0777 /workspace/vue /workspace/vue/node_modules node_modules/.tmp

COPY --chown=node:node . .
CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0"]

# 型・lint・unit test・production bundleを一度ずつ検証する
FROM development AS check
RUN pnpm run check:full

# 配信runtime
FROM nginx:stable-alpine@sha256:97d490c12ba55b4946b01546d1c3ed324e8d41ab1c9fcb2a616aa470620e5b46 AS web-runtime
COPY --from=check /workspace/vue/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]

# Playwright専用のHTTP配信環境。API responseはbrowser側でinterceptする。
FROM web-runtime AS e2e-http
COPY nginx.e2e.conf /etc/nginx/nginx.conf
EXPOSE 80

# 本番環境。既定build targetをproductionに保つため最後に配置する。
FROM web-runtime AS production
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
