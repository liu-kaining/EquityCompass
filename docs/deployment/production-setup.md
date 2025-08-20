# 智策股析 - 生产环境配置指南

本文档详细说明如何将智策股析项目部署到生产环境。

## 🚀 生产环境部署清单

### 1. 环境变量配置

创建 `.env` 文件（生产环境）：

```bash
# ===== 基础配置 =====
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this

# ===== 数据库配置 =====
DATABASE_URL=postgresql://username:password@localhost:5432/equitycompass

# ===== Redis配置 =====
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ===== 邮件服务配置 =====
# Gmail配置示例
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=智策股析
SEND_EMAIL=true

# QQ邮箱配置示例
# SMTP_SERVER=smtp.qq.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@qq.com
# SMTP_PASSWORD=your-authorization-code

# ===== LLM API配置 =====
OPENAI_API_KEY=sk-your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
QWEN_API_KEY=your-qwen-api-key

# ===== 支付网关配置 =====
STRIPE_PUBLIC_KEY=pk_test_your-stripe-public-key
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# ===== 金融数据API配置 =====
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
FINNHUB_API_KEY=your-finnhub-key

# ===== 安全配置 =====
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. 数据库配置

#### PostgreSQL 安装和配置

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql postgresql-server
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew install postgresql
brew services start postgresql
```

#### 创建数据库和用户

```sql
-- 连接到PostgreSQL
sudo -u postgres psql

-- 创建数据库
CREATE DATABASE equitycompass;

-- 创建用户
CREATE USER equitycompass_user WITH PASSWORD 'your-secure-password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE equitycompass TO equitycompass_user;

-- 退出
\q
```

#### 安装Python PostgreSQL驱动

```bash
pip install psycopg2-binary
```

### 3. Redis 配置

#### 安装Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server

# CentOS/RHEL
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis

# macOS
brew install redis
brew services start redis
```

#### Redis安全配置

编辑 `/etc/redis/redis.conf`：

```conf
# 设置密码
requirepass your-redis-password

# 绑定到本地
bind 127.0.0.1

# 禁用危险命令
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# 设置最大内存
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 4. 邮件服务配置

#### Gmail配置

1. 开启两步验证
2. 生成应用专用密码
3. 使用应用专用密码作为 `SMTP_PASSWORD`

#### QQ邮箱配置

1. 开启SMTP服务
2. 获取授权码
3. 使用授权码作为 `SMTP_PASSWORD`

#### 域名邮箱配置

```bash
# 示例：使用自己的域名邮箱
SMTP_SERVER=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=your-email-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=智策股析
```

### 5. Web服务器配置

#### Nginx 配置

```nginx
# /etc/nginx/sites-available/equitycompass
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 静态文件
    location /static/ {
        alias /path/to/equitycompass/backend/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 代理到Flask应用
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Gunicorn 配置

```python
# gunicorn.conf.py
bind = "127.0.0.1:5001"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

### 6. 系统服务配置

#### 创建系统服务

```bash
# /etc/systemd/system/equitycompass.service
[Unit]
Description=EquityCompass Flask Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=equitycompass
Group=equitycompass
WorkingDirectory=/path/to/equitycompass/backend
Environment=PATH=/path/to/equitycompass/backend/venv/bin
Environment=FLASK_ENV=production
ExecStart=/path/to/equitycompass/backend/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable equitycompass
sudo systemctl start equitycompass
sudo systemctl status equitycompass
```

### 7. SSL证书配置

#### Let's Encrypt 免费证书

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. 监控和日志

#### 日志配置

```python
# 在app/__init__.py中添加
import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/equitycompass.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('EquityCompass startup')
```

#### 健康检查

```bash
# 创建健康检查脚本
#!/bin/bash
# /usr/local/bin/health-check.sh

curl -f http://localhost:5001/api/health || exit 1
```

### 9. 备份策略

#### 数据库备份

```bash
#!/bin/bash
# /usr/local/bin/backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/database"
mkdir -p $BACKUP_DIR

pg_dump equitycompass > $BACKUP_DIR/equitycompass_$DATE.sql
gzip $BACKUP_DIR/equitycompass_$DATE.sql

# 保留最近30天的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

#### 文件备份

```bash
#!/bin/bash
# /usr/local/bin/backup-files.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/files"
SOURCE_DIR="/path/to/equitycompass/data"

tar -czf $BACKUP_DIR/equitycompass_files_$DATE.tar.gz -C $SOURCE_DIR .
```

### 10. 安全配置

#### 防火墙配置

```bash
# UFW防火墙
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

#### 系统安全

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装安全工具
sudo apt install fail2ban ufw

# 配置fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 11. 性能优化

#### 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_stocks_code ON stocks(code);
CREATE INDEX idx_user_watchlists_user_id ON user_watchlists(user_id);

-- 分析表
ANALYZE users;
ANALYZE stocks;
ANALYZE user_watchlists;
```

#### Redis优化

```conf
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 12. 部署检查清单

- [ ] 环境变量配置完成
- [ ] 数据库安装和配置
- [ ] Redis安装和配置
- [ ] 邮件服务配置
- [ ] SSL证书安装
- [ ] Nginx配置
- [ ] Gunicorn配置
- [ ] 系统服务启动
- [ ] 日志配置
- [ ] 备份策略
- [ ] 安全配置
- [ ] 性能优化
- [ ] 功能测试

### 13. 常见问题

#### 邮件发送失败
- 检查SMTP配置
- 确认邮箱开启SMTP服务
- 验证应用专用密码

#### 数据库连接失败
- 检查PostgreSQL服务状态
- 验证数据库连接字符串
- 确认用户权限

#### Redis连接失败
- 检查Redis服务状态
- 验证Redis密码配置
- 确认网络连接

---

*最后更新: 2025-08-20*
*维护者: 智策股析开发团队*
