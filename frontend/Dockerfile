# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# 复制 package.json 和 lock 文件
COPY package*.json ./
RUN npm install

# 复制前端代码并构建
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:stable-alpine

# 复制构建产物到 Nginx 目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
