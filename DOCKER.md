# Docker部署说明

## 快速开始

### 1. 环境准备
- 安装Docker和Docker Compose
- 确保端口5002可用

### 2. 部署步骤

```bash
# 克隆项目
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass

# 配置环境变量
cp backend/env.example .env
# 编辑.env文件，配置API密钥

# 启动服务
docker-compose up -d --build

# 初始化数据
docker exec -it equitycompass-app python app.py init-db
docker exec -it equitycompass-app python scripts/import_stocks.py
```

### 3. 访问应用
打开浏览器访问: http://localhost:5002

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 进入容器
docker exec -it equitycompass-app bash

# 更新代码后重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 数据持久化

- 应用数据: `equitycompass_data` 卷
- 日志文件: `equitycompass_logs` 卷
- 数据库文件: 容器内持久化

## 故障排除

### 常见问题

1. **容器启动失败**
```bash
docker-compose logs equitycompass
```

2. **端口冲突**
```bash
# 检查端口占用
netstat -tlnp | grep 5002
```

3. **API调用失败**
```bash
# 检查API密钥配置
docker exec -it equitycompass-app env | grep API_KEY
```

## 生产环境建议

1. 使用反向代理（Nginx）
2. 配置SSL证书
3. 设置资源限制
4. 定期备份数据
5. 监控容器健康状态
