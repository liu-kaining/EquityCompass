# Docker部署指南

## 概述

本文档详细说明如何使用Docker部署EquityCompass股票分析平台。

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB可用内存
- 至少10GB可用磁盘空间

## 快速部署

### 1. 获取代码

```bash
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp backend/env.example .env

# 编辑配置文件
nano .env
```

主要配置项：
```bash
# Flask配置
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# AI模型API密钥
GEMINI_API_KEY=your-gemini-api-key
QWEN_API_KEY=your-qwen-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 3. 启动服务

```bash
# 构建并启动容器
docker-compose up -d --build

# 查看启动状态
docker-compose ps
```

### 4. 初始化数据

```bash
# 进入容器
docker exec -it equitycompass-app bash

# 初始化数据库
python app.py init-db

# 导入股票数据
python scripts/import_stocks.py

# 退出容器
exit
```

### 5. 访问应用

打开浏览器访问：http://localhost:5001

## 生产环境部署

### 1. 服务器准备

#### 安装Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### 安装Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 安全配置

#### 创建专用用户
```bash
sudo useradd -m -s /bin/bash equitycompass
sudo usermod -aG docker equitycompass
```

#### 配置防火墙
```bash
# 开放必要端口
sudo ufw allow 5001/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 3. 部署应用

```bash
# 切换到专用用户
sudo su - equitycompass

# 克隆项目
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass

# 配置环境变量
cp backend/env.example .env
nano .env

# 启动服务
docker-compose up -d --build
```

### 4. 配置反向代理（可选）

#### 使用Nginx
```bash
# 安装Nginx
sudo apt update
sudo apt install nginx

# 创建配置文件
sudo nano /etc/nginx/sites-available/equitycompass
```

Nginx配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/equitycompass /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 容器管理

### 常用命令

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f equitycompass

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 进入容器
docker exec -it equitycompass-app bash

# 查看容器资源使用
docker stats equitycompass-app
```

### 数据备份

```bash
# 备份数据卷
docker run --rm -v equitycompass_data:/data -v $(pwd):/backup alpine tar czf /backup/data_backup.tar.gz -C /data .

# 备份日志
docker run --rm -v equitycompass_logs:/logs -v $(pwd):/backup alpine tar czf /backup/logs_backup.tar.gz -C /logs .
```

### 数据恢复

```bash
# 恢复数据
docker run --rm -v equitycompass_data:/data -v $(pwd):/backup alpine tar xzf /backup/data_backup.tar.gz -C /data

# 恢复日志
docker run --rm -v equitycompass_logs:/logs -v $(pwd):/backup alpine tar xzf /backup/logs_backup.tar.gz -C /logs
```

## 监控和维护

### 健康检查

容器内置健康检查，可通过以下方式监控：

```bash
# 查看健康状态
docker inspect equitycompass-app | grep Health -A 10

# 设置监控脚本
cat > /home/equitycompass/monitor.sh << 'EOF'
#!/bin/bash
if ! docker inspect equitycompass-app | grep -q '"Status": "healthy"'; then
    echo "$(date): Container is unhealthy, restarting..." >> /home/equitycompass/monitor.log
    docker-compose restart
fi
EOF

chmod +x /home/equitycompass/monitor.sh

# 添加到crontab
echo "*/5 * * * * /home/equitycompass/monitor.sh" | crontab -
```

### 日志管理

```bash
# 查看应用日志
docker-compose logs -f equitycompass

# 查看容器日志
docker logs -f equitycompass-app

# 清理旧日志
docker system prune -f
```

### 性能优化

#### 资源限制
在docker-compose.yml中添加资源限制：

```yaml
services:
  equitycompass:
    # ... 其他配置
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

#### 数据库优化
```bash
# 进入容器优化数据库
docker exec -it equitycompass-app bash
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.engine.execute('PRAGMA journal_mode=WAL;')
    db.engine.execute('PRAGMA synchronous=NORMAL;')
    db.engine.execute('PRAGMA cache_size=10000;')
    db.engine.execute('PRAGMA temp_store=MEMORY;')
"
```

## 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看详细错误信息
docker-compose logs equitycompass

# 检查端口占用
netstat -tlnp | grep 5001

# 检查磁盘空间
df -h
```

#### 2. 数据库连接失败
```bash
# 检查数据库文件权限
docker exec -it equitycompass-app ls -la instance/

# 重新初始化数据库
docker exec -it equitycompass-app python app.py init-db
```

#### 3. AI模型调用失败
```bash
# 检查API密钥配置
docker exec -it equitycompass-app env | grep API_KEY

# 查看AI调用日志
docker exec -it equitycompass-app tail -f logs/app.log
```

#### 4. PDF导出失败
```bash
# 检查Playwright安装
docker exec -it equitycompass-app playwright --version

# 重新安装Playwright
docker exec -it equitycompass-app playwright install chromium
```

### 日志分析

```bash
# 查看错误日志
docker exec -it equitycompass-app grep -i error logs/app.log

# 查看AI调用统计
docker exec -it equitycompass-app grep "API调用" logs/app.log | wc -l

# 查看性能日志
docker exec -it equitycompass-app grep "响应时间" logs/app.log
```

## 更新部署

### 代码更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 检查服务状态
docker-compose ps
```

### 配置更新
```bash
# 更新环境变量
nano .env

# 重启服务
docker-compose restart
```

## 安全建议

1. **定期更新**：定期更新Docker镜像和系统包
2. **密钥管理**：使用安全的密钥管理服务
3. **网络隔离**：使用Docker网络隔离应用
4. **访问控制**：限制容器访问权限
5. **日志审计**：定期检查安全日志

## 性能基准

### 推荐配置
- CPU: 2核心以上
- 内存: 4GB以上
- 磁盘: SSD 20GB以上
- 网络: 100Mbps以上

### 性能指标
- 并发用户: 50+
- 响应时间: <2秒
- 内存使用: <2GB
- 磁盘使用: <5GB

---

更多部署相关问题，请查看项目Issues或联系维护者。
