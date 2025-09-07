# EquityCompass Docker 部署指南

## 概述

本指南详细说明如何使用Docker部署EquityCompass股票分析平台的最新版本。

## 系统要求

- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **内存**: 至少2GB可用内存
- **磁盘**: 至少10GB可用磁盘空间
- **网络**: 稳定的互联网连接（用于AI模型API调用）

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

**重要配置项**：
```bash
# Flask配置
FLASK_SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
FLASK_ENV=production

# AI模型API密钥（至少配置一个）
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-reasoner
DEFAULT_AI_PROVIDER=deepseek

# 可选的其他AI模型
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
QWEN_API_KEY=your-qwen-api-key-here
QWEN_MODEL=qwen-deep-research
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-pro

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@equitycompass.com
ADMIN_PASSWORD=admin123456
ADMIN_NICKNAME=系统管理员

# 数据库配置
DATABASE_URL=sqlite:///dev.db

# 邮件配置（可选）
SEND_EMAIL=False
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. 启动服务

```bash
# 构建并启动容器
docker-compose up -d --build

# 查看启动状态
docker-compose ps
```

### 4. 查看启动日志

```bash
# 查看实时日志
docker-compose logs -f equitycompass

# 查看容器状态
docker-compose ps
```

### 5. 访问应用

打开浏览器访问：**http://localhost:5002**

**默认登录信息**：
- 用户名：`admin`
- 密码：`admin123456`
- 邮箱：`admin@equitycompass.com`

## 生产环境部署

### 1. 服务器准备

#### 安装Docker和Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

#### 创建专用用户

```bash
sudo useradd -m -s /bin/bash equitycompass
sudo usermod -aG docker equitycompass
sudo su - equitycompass
```

#### 配置防火墙

```bash
# 开放必要端口
sudo ufw allow 5002/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 2. 部署应用

```bash
# 克隆项目
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass

# 配置环境变量
cp backend/env.example .env
nano .env  # 编辑配置文件

# 启动服务
docker-compose up -d --build
```

### 3. 配置反向代理（推荐）

#### 使用Nginx

```bash
# 安装Nginx
sudo apt update
sudo apt install nginx

# 创建配置文件
sudo nano /etc/nginx/sites-available/equitycompass
```

**Nginx配置示例**：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
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

# 更新代码后重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 数据备份

```bash
# 备份数据卷
docker run --rm -v equitycompass_data:/data -v $(pwd):/backup alpine tar czf /backup/data_backup_$(date +%Y%m%d).tar.gz -C /data .

# 备份日志
docker run --rm -v equitycompass_logs:/logs -v $(pwd):/backup alpine tar czf /backup/logs_backup_$(date +%Y%m%d).tar.gz -C /logs .
```

### 数据恢复

```bash
# 恢复数据
docker run --rm -v equitycompass_data:/data -v $(pwd):/backup alpine tar xzf /backup/data_backup_20240101.tar.gz -C /data

# 恢复日志
docker run --rm -v equitycompass_logs:/logs -v $(pwd):/backup alpine tar xzf /backup/logs_backup_20240101.tar.gz -C /logs
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

# 添加到crontab（每5分钟检查一次）
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

在`docker-compose.yml`中添加资源限制：

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
netstat -tlnp | grep 5002

# 检查磁盘空间
df -h

# 检查Docker服务状态
sudo systemctl status docker
```

#### 2. 数据库连接失败

```bash
# 检查数据库文件权限
docker exec -it equitycompass-app ls -la instance/

# 重新初始化数据库
docker exec -it equitycompass-app python app.py init-db

# 检查数据库文件
docker exec -it equitycompass-app sqlite3 instance/dev.db ".tables"
```

#### 3. AI模型调用失败

```bash
# 检查API密钥配置
docker exec -it equitycompass-app env | grep API_KEY

# 查看AI调用日志
docker exec -it equitycompass-app tail -f logs/app.log

# 测试AI配置
docker exec -it equitycompass-app python -c "
from app import create_app
from app.services.ai.llm_provider import LLMProvider
app = create_app()
with app.app_context():
    provider = LLMProvider()
    print('Available providers:', provider.get_available_providers())
"
```

#### 4. PDF导出失败

```bash
# 检查Playwright安装
docker exec -it equitycompass-app playwright --version

# 重新安装Playwright
docker exec -it equitycompass-app playwright install chromium

# 检查Chromium
docker exec -it equitycompass-app which chromium
```

#### 5. 任务管理功能异常

```bash
# 检查任务文件
docker exec -it equitycompass-app ls -la data/tasks/

# 查看任务管理日志
docker exec -it equitycompass-app grep -i "task" logs/app.log

# 重启任务管理服务
docker-compose restart
```

### 日志分析

```bash
# 查看错误日志
docker exec -it equitycompass-app grep -i error logs/app.log

# 查看AI调用统计
docker exec -it equitycompass-app grep "API调用" logs/app.log | wc -l

# 查看性能日志
docker exec -it equitycompass-app grep "响应时间" logs/app.log

# 查看任务执行日志
docker exec -it equitycompass-app grep "任务" logs/app.log
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

### 数据库迁移

```bash
# 进入容器
docker exec -it equitycompass-app bash

# 运行数据库迁移
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('数据库迁移完成')
"
```

## 安全建议

1. **定期更新**：定期更新Docker镜像和系统包
2. **密钥管理**：使用安全的密钥管理服务，不要在代码中硬编码API密钥
3. **网络隔离**：使用Docker网络隔离应用
4. **访问控制**：限制容器访问权限，使用非root用户运行
5. **日志审计**：定期检查安全日志
6. **备份策略**：定期备份数据和配置
7. **监控告警**：设置监控告警，及时发现异常

## 性能基准

### 推荐配置

- **CPU**: 2核心以上
- **内存**: 4GB以上
- **磁盘**: SSD 20GB以上
- **网络**: 100Mbps以上

### 性能指标

- **并发用户**: 50+
- **响应时间**: <2秒
- **内存使用**: <2GB
- **磁盘使用**: <5GB

## 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `FLASK_SECRET_KEY` | Flask密钥 | - | 是 |
| `JWT_SECRET_KEY` | JWT密钥 | - | 是 |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | - | 是* |
| `OPENAI_API_KEY` | OpenAI API密钥 | - | 否 |
| `QWEN_API_KEY` | 通义千问API密钥 | - | 否 |
| `GEMINI_API_KEY` | Gemini API密钥 | - | 否 |
| `DEFAULT_AI_PROVIDER` | 默认AI提供商 | deepseek | 否 |
| `ADMIN_EMAIL` | 管理员邮箱 | admin@equitycompass.com | 否 |
| `ADMIN_PASSWORD` | 管理员密码 | admin123456 | 否 |
| `DATABASE_URL` | 数据库URL | sqlite:///dev.db | 否 |
| `SEND_EMAIL` | 是否发送邮件 | False | 否 |

*至少需要配置一个AI模型的API密钥

## 联系支持

如果在部署过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查项目的Issues页面
3. 联系项目维护者

---

**注意**：本指南基于EquityCompass的最新版本编写，请确保使用最新的代码和配置。
