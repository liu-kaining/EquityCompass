# Ubuntu 22.04 + Python 3.9 + 国内 PyPI 镜像
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=5002

# 系统依赖 + 软链 python → python3
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.9 \
        python3-pip \
        python3-venv \
        curl wget gnupg ca-certificates fonts-liberation \
        libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 \
        libcups2 libdbus-1-3 libdrm2 libgtk-3-0 libnspr4 libnss3 \
        libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxss1 \
        libxtst6 xdg-utils libx11-xcb1 libxcb-dri3-0 libxkbcommon0 \
        libxshmfence1 && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制并安装 Python 依赖（清华镜像）
COPY backend/requirements.txt .
RUN pip install --no-cache-dir \
        -i https://pypi.tuna.tsinghua.edu.cn/simple \
        -r requirements.txt

# Playwright & Chromium（单独安装避免依赖冲突）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple playwright==1.54.0 && \
    playwright install chromium && \
    playwright install-deps chromium

# 复制代码与启动脚本
COPY backend/ .
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# 确保requirements.txt存在
RUN test -f requirements.txt || (echo "requirements.txt not found" && exit 1)

# 创建目录并赋权
RUN mkdir -p data/reports data/tasks data/usage logs && \
    chmod -R 755 data logs && \
    chmod +x /app/docker-entrypoint.sh

EXPOSE 5002

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/ || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
