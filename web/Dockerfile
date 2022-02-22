# ビルド環境
FROM node:14.19-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 本番環境
FROM nginx:stable-alpine as production-stage
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]