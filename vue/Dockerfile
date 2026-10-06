# 前端镜像（多阶段：node 构建 → nginx 托管 dist；build context = 仓库根）
FROM node:18-alpine AS build
WORKDIR /app
COPY vue/package.json vue/package-lock.json* ./
RUN npm install
COPY vue ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY vue/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
