# 使用轻量级 Node 镜像
FROM node:20-alpine

WORKDIR /app

# 1. 安装一个超小的静态文件服务器 "serve"
RUN npm install -g serve

# 2. 复制依赖并安装
COPY package*.json ./
RUN npm install

# 3. 复制源码并打包
COPY . .
RUN npm run build

# 4. 暴露端口 (serve 默认可以用 3000，我们指定用 80)
EXPOSE 80


# 5. 启动命令：用 serve 运行 dist 目录，端口 80
CMD ["serve", "-s", "dist", "-l", "80"]