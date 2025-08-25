# 使用Python 3.9官方镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=5002

# 安装系统依赖（包括Playwright所需的依赖）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxkbcommon0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# 安装Playwright和浏览器
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# 复制requirements.txt
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ .

# 复制启动脚本
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# 创建必要的目录
RUN mkdir -p data/reports data/tasks data/usage logs

# 设置目录权限和脚本执行权限
RUN chmod -R 755 data logs && \
    chmod +x /app/docker-entrypoint.sh

# 暴露端口
EXPOSE 5002

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/ || exit 1

# 使用启动脚本
ENTRYPOINT ["/app/docker-entrypoint.sh"]
