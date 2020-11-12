# ビルド環境
FROM node:lts-alpine as build-stage
WORKDIR /app
ADD package*.json ./
RUN npm install
ADD . .
RUN npm run build

# 本番環境
FROM nginx:stable-alpine as production-stage
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]