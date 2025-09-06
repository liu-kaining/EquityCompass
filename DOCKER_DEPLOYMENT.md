# Docker 部署指南

## 🐳 概述

本文档详细说明如何使用Docker部署智策股析(EquityCompass)系统。

## 📋 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB可用内存
- 至少5GB可用磁盘空间

## 🚀 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
cp env.example .env
```

编辑 `.env` 文件，配置必要的环境变量：

```bash
# 基本配置
FLASK_SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///dev.db

# AI模型配置
DEEPSEEK_API_KEY=your-deepseek-api-key
OPENAI_API_KEY=your-openai-api-key
QWEN_API_KEY=your-qwen-api-key
GEMINI_API_KEY=your-gemini-api-key

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@equitycompass.com
ADMIN_PASSWORD=admin123456
ADMIN_NICKNAME=系统管理员

# 邮件配置（可选）
SEND_EMAIL=False
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. 构建并启动

```bash
# 构建并启动服务
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

### 4. 验证部署

访问 http://localhost:5002 验证部署是否成功。

默认管理员账户：
- 用户名: admin
- 密码: admin123456

## 🔧 详细配置

### 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `FLASK_SECRET_KEY` | ✅ | - | Flask应用密钥 |
| `JWT_SECRET_KEY` | ✅ | - | JWT令牌密钥 |
| `DATABASE_URL` | ❌ | sqlite:///dev.db | 数据库连接URL |
| `DEEPSEEK_API_KEY` | ❌ | - | DeepSeek API密钥 |
| `OPENAI_API_KEY` | ❌ | - | OpenAI API密钥 |
| `QWEN_API_KEY` | ❌ | - | 通义千问API密钥 |
| `GEMINI_API_KEY` | ❌ | - | Google Gemini API密钥 |
| `ADMIN_USERNAME` | ❌ | admin | 管理员用户名 |
| `ADMIN_EMAIL` | ❌ | admin@equitycompass.com | 管理员邮箱 |
| `ADMIN_PASSWORD` | ❌ | admin123456 | 管理员密码 |
| `ADMIN_NICKNAME` | ❌ | 系统管理员 | 管理员昵称 |
| `SEND_EMAIL` | ❌ | False | 是否启用邮件发送 |

### 数据持久化

系统使用Docker volumes进行数据持久化：

- `equitycompass_data`: 存储应用数据（数据库、报告、任务等）
- `equitycompass_logs`: 存储应用日志

### 健康检查

容器包含健康检查机制：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5002/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

## 🛠️ 管理命令

### 查看服务状态

```bash
# 查看容器状态
docker-compose ps

# 查看服务日志
docker-compose logs -f equitycompass

# 查看实时日志
docker-compose logs -f --tail=100
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart equitycompass
```

### 更新服务

```bash
# 停止服务
docker-compose down

# 重新构建镜像
docker-compose build --no-cache

# 启动服务
docker-compose up -d
```

### 数据备份

```bash
# 备份数据卷
docker run --rm -v equitycompass_data:/data -v $(pwd):/backup ubuntu tar czf /backup/equitycompass_data_backup.tar.gz -C /data .

# 恢复数据卷
docker run --rm -v equitycompass_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/equitycompass_data_backup.tar.gz -C /data
```

## 🔍 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 查看详细错误日志
   docker-compose logs equitycompass
   
   # 检查环境变量配置
   docker-compose config
   ```

2. **数据库初始化失败**
   ```bash
   # 进入容器手动初始化
   docker-compose exec equitycompass bash
   python scripts/init_db.py
   python scripts/import_stocks.py
   python scripts/setup_admin_user.py
   python scripts/init_ai_configs.py
   ```

3. **AI模型连接失败**
   - 检查API密钥是否正确配置
   - 确认网络连接正常
   - 查看应用日志中的错误信息

4. **端口冲突**
   ```bash
   # 修改docker-compose.yml中的端口映射
   ports:
     - "8080:5002"  # 改为其他端口
   ```

### 日志查看

```bash
# 查看应用日志
docker-compose logs equitycompass

# 查看特定时间段的日志
docker-compose logs --since="2024-01-01T00:00:00" equitycompass

# 查看错误日志
docker-compose logs equitycompass 2>&1 | grep -i error
```

## 🔒 安全配置

### 生产环境安全建议

1. **更改默认密钥**
   ```bash
   # 生成强密钥
   openssl rand -hex 32
   ```

2. **使用HTTPS**
   - 配置反向代理（Nginx）
   - 使用Let's Encrypt证书

3. **限制网络访问**
   ```yaml
   # 在docker-compose.yml中添加
   networks:
     - internal
   
   networks:
     internal:
       driver: bridge
   ```

4. **定期备份**
   - 设置自动备份脚本
   - 测试备份恢复流程

## 📊 监控和维护

### 资源监控

```bash
# 查看容器资源使用情况
docker stats equitycompass-app

# 查看磁盘使用情况
docker system df
```

### 日志轮转

```bash
# 配置日志轮转
docker-compose exec equitycompass bash
# 在容器内配置logrotate
```

### 性能优化

1. **数据库优化**
   - 定期清理旧数据
   - 优化查询索引

2. **缓存配置**
   - 启用Redis缓存
   - 配置静态资源缓存

## 🚀 生产环境部署

### 使用Nginx反向代理

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
    }
}
```

### 使用Docker Swarm

```bash
# 初始化Swarm
docker swarm init

# 部署服务栈
docker stack deploy -c docker-compose.yml equitycompass
```

## 📞 技术支持

如遇到部署问题，请：

1. 查看本文档的故障排除部分
2. 检查GitHub Issues
3. 联系技术支持团队

---

**智策股析** - Docker部署指南 🐳
