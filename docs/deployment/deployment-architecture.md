# 智策股析 - 部署架构设计

## 部署架构概述

智策股析采用现代化的云原生部署架构，支持从开发到生产的完整生命周期管理。

## 开发环境架构

### 环境概述
开发环境注重快速迭代和调试便利性，采用简化的单机部署方案。

### 核心组件

#### 开发服务
```
前端开发服务器 (React/Vue Dev Server)
├── 端口: 3000
├── 热重载: 启用
├── 代理配置: 转发 /api 到后端
└── 环境变量: REACT_APP_API_URL=http://localhost:5000

后端开发服务器 (Flask Development Server)
├── 端口: 5000
├── 调试模式: 启用
├── 自动重启: 文件变更触发
└── 环境变量: FLASK_ENV=development
```

#### 开发数据存储
```
SQLite数据库
├── 文件路径: ./data/dev.db
├── 轻量级: 适合开发调试
└── 版本控制: schema.sql纳入git

Redis容器
├── 端口: 6379
├── 容器运行: docker run -p 6379:6379 redis:alpine
├── 数据持久化: 关闭（开发环境）
└── 配置: 默认配置即可

本地文件存储
├── 报告目录: ./data/reports/
├── 导出目录: ./data/exports/
├── 日志目录: ./logs/
└── 权限: 开发用户可读写
```

#### 模拟外部服务
```
模拟邮件服务
├── 实现方式: 控制台输出
├── 验证码: 打印到终端
└── 邮件内容: 保存到本地文件

模拟支付服务
├── 支付结果: 总是返回成功
├── 回调处理: 本地webhook端点
└── 测试数据: 固定测试用例

真实LLM API
├── 使用环境: 开发专用API Key
├── 请求限制: 较低配额
└── 模型选择: 基础版本模型
```

### 开发环境启动流程
```bash
# 1. 启动Redis
docker run -d -p 6379:6379 --name redis-dev redis:alpine

# 2. 初始化数据库
cd backend
python manage.py init-db

# 3. 启动Celery Worker
celery -A app.celery worker --loglevel=info

# 4. 启动后端服务
python app.py

# 5. 启动前端服务
cd frontend
npm run dev
```

---

## 生产环境架构

### 架构概述
生产环境采用高可用、可扩展的分布式架构，支持大规模用户访问。

### 负载均衡层

#### Nginx负载均衡器
```nginx
upstream backend_servers {
    least_conn;
    server backend-1:5000 weight=3;
    server backend-2:5000 weight=3;
    server backend-3:5000 weight=2;
}

upstream frontend_servers {
    server frontend-1:80;
    server frontend-2:80;
}

server {
    listen 443 ssl http2;
    server_name app.equitycompass.com;
    
    # SSL配置
    ssl_certificate /etc/ssl/certs/app.crt;
    ssl_certificate_key /etc/ssl/private/app.key;
    
    # API请求转发
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件服务
    location / {
        proxy_pass http://frontend_servers;
        proxy_set_header Host $host;
    }
}
```

#### SSL证书管理
```bash
# Let's Encrypt自动续期
certbot certonly --nginx \
    -d app.equitycompass.com \
    -d api.equitycompass.com

# 自动续期Cron任务
0 12 * * * /usr/bin/certbot renew --quiet
```

### Web服务层

#### Flask应用服务器
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend-1:
    image: equitycompass/backend:latest
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@postgres:5432/equitycompass
      - REDIS_URL=redis://redis-cluster:6379/0
      - CELERY_BROKER_URL=redis://redis-cluster:6379/1
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Gunicorn配置
```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 60
preload_app = True
```

### 异步任务层

#### Celery Worker配置
```yaml
celery-worker:
  image: equitycompass/backend:latest
  command: celery -A app.celery worker --loglevel=info --concurrency=4
  environment:
    - CELERY_BROKER_URL=redis://redis-cluster:6379/1
    - DATABASE_URL=postgresql://user:pass@postgres:5432/equitycompass
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
  volumes:
    - /data/reports:/app/data/reports
```

#### Celery Beat调度器
```yaml
celery-beat:
  image: equitycompass/backend:latest
  command: celery -A app.celery beat --loglevel=info
  environment:
    - CELERY_BROKER_URL=redis://redis-cluster:6379/1
  deploy:
    replicas: 1  # 只能有一个实例
```

#### Flower任务监控
```yaml
flower:
  image: mher/flower
  command: celery flower --broker=redis://redis-cluster:6379/1
  ports:
    - "5555:5555"
  environment:
    - FLOWER_BASIC_AUTH=admin:secure_password
```

### 数据存储层

#### PostgreSQL主从集群
```yaml
# 主数据库
postgres-master:
  image: postgres:14
  environment:
    POSTGRES_DB: equitycompass
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: secure_password
    POSTGRES_REPLICATION_USER: replicator
    POSTGRES_REPLICATION_PASSWORD: repl_password
  volumes:
    - postgres_master_data:/var/lib/postgresql/data
    - ./postgresql.conf:/etc/postgresql/postgresql.conf
  command: |
    postgres -c config_file=/etc/postgresql/postgresql.conf

# 从数据库
postgres-slave:
  image: postgres:14
  environment:
    PGUSER: postgres
    POSTGRES_PASSWORD: secure_password
    POSTGRES_MASTER_SERVICE: postgres-master
  volumes:
    - postgres_slave_data:/var/lib/postgresql/data
  command: |
    bash -c "
    until pg_basebackup -h postgres-master -D /var/lib/postgresql/data -U replicator -v -P -W
    do
      echo 'Waiting for master to be available...'
      sleep 1s
    done
    echo 'standby_mode = on' >> /var/lib/postgresql/data/recovery.conf
    echo 'primary_conninfo = host=postgres-master port=5432 user=replicator' >> /var/lib/postgresql/data/recovery.conf
    postgres
    "
```

#### Redis集群
```yaml
redis-cluster:
  image: redis:7-alpine
  command: redis-server --appendonly yes --cluster-enabled yes
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  deploy:
    replicas: 3
```

#### 文件存储
```yaml
# 方案1: 本地NFS存储
volumes:
  reports_data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nfs-server,rw,sync
      device: ":/data/reports"

# 方案2: AWS S3存储
# 环境变量配置
AWS_ACCESS_KEY_ID: your_access_key
AWS_SECRET_ACCESS_KEY: your_secret_key
AWS_DEFAULT_REGION: us-west-2
S3_BUCKET_NAME: equitycompass-reports
```

### 监控告警系统

#### Prometheus监控
```yaml
prometheus:
  image: prom/prometheus:latest
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--web.console.libraries=/etc/prometheus/console_libraries'
    - '--web.console.templates=/etc/prometheus/consoles'
    - '--storage.tsdb.retention.time=200h'
    - '--web.enable-lifecycle'
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"
```

#### Grafana监控面板
```yaml
grafana:
  image: grafana/grafana:latest
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin_password
    - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
  volumes:
    - grafana_data:/var/lib/grafana
    - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
  ports:
    - "3000:3000"
```

#### ELK日志系统
```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
  environment:
    - discovery.type=single-node
    - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
  volumes:
    - elasticsearch_data:/usr/share/elasticsearch/data

logstash:
  image: docker.elastic.co/logstash/logstash:8.5.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
  image: docker.elastic.co/kibana/kibana:8.5.0
  environment:
    - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
  ports:
    - "5601:5601"
```

### 部署自动化

#### CI/CD流水线 (GitHub Actions)
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          python -m pytest backend/tests/
          npm test --prefix frontend/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker Images
        run: |
          docker build -t equitycompass/backend:latest ./backend
          docker build -t equitycompass/frontend:latest ./frontend
      - name: Push to Registry
        run: |
          docker push equitycompass/backend:latest
          docker push equitycompass/frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Production
        run: |
          ssh production-server "
            cd /opt/equitycompass
            docker-compose pull
            docker-compose up -d --no-deps backend frontend
            docker-compose exec backend python manage.py migrate
          "
```

#### 蓝绿部署
```bash
#!/bin/bash
# blue-green-deploy.sh

CURRENT_ENV=$(docker-compose ps | grep backend | head -1 | awk '{print $1}' | grep -o 'blue\|green')
NEW_ENV=$([ "$CURRENT_ENV" = "blue" ] && echo "green" || echo "blue")

echo "当前环境: $CURRENT_ENV, 新环境: $NEW_ENV"

# 启动新环境
docker-compose -f docker-compose.$NEW_ENV.yml up -d

# 健康检查
sleep 30
if curl -f http://localhost:5001/api/health; then
    echo "新环境健康检查通过，切换流量"
    # 更新负载均衡器配置
    sed -i "s/backend-$CURRENT_ENV/backend-$NEW_ENV/g" nginx.conf
    nginx -s reload
    
    # 停止旧环境
    docker-compose -f docker-compose.$CURRENT_ENV.yml down
else
    echo "新环境健康检查失败，回滚"
    docker-compose -f docker-compose.$NEW_ENV.yml down
    exit 1
fi
```

### 安全配置

#### 网络安全
```yaml
# 网络隔离
networks:
  frontend_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
  backend_network:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.21.0.0/16

# 服务网络配置
services:
  nginx:
    networks:
      - frontend_network
  backend:
    networks:
      - frontend_network
      - backend_network
  database:
    networks:
      - backend_network  # 仅内网访问
```

#### 环境变量管理
```bash
# 使用外部secrets管理
docker swarm init
echo "database_password" | docker secret create db_password -
echo "jwt_secret_key" | docker secret create jwt_secret -

# 在服务中使用secrets
services:
  backend:
    secrets:
      - db_password
      - jwt_secret
    environment:
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password
      - JWT_SECRET_KEY_FILE=/run/secrets/jwt_secret
```

### 备份策略

#### 数据库备份
```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份
pg_dump -h postgres-master -U postgres equitycompass > "$BACKUP_DIR/backup_$DATE.sql"

# 压缩备份文件
gzip "$BACKUP_DIR/backup_$DATE.sql"

# 删除7天前的备份
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +7 -delete

# 上传到云存储
aws s3 cp "$BACKUP_DIR/backup_$DATE.sql.gz" s3://equitycompass-backups/database/
```

#### 文件备份
```bash
#!/bin/bash
# backup-files.sh

REPORTS_DIR="/data/reports"
BACKUP_DIR="/backups/files"
DATE=$(date +%Y%m%d)

# 增量备份（仅备份今天的文件）
rsync -av --include="*/$DATE/" --include="*/$DATE/*" --exclude="*" \
    "$REPORTS_DIR/" "$BACKUP_DIR/incremental/$DATE/"

# 每周全量备份
if [ $(date +%u) -eq 7 ]; then
    tar -czf "$BACKUP_DIR/full/reports_$DATE.tar.gz" "$REPORTS_DIR"
    aws s3 cp "$BACKUP_DIR/full/reports_$DATE.tar.gz" s3://equitycompass-backups/files/
fi
```

### 性能优化

#### 应用层优化
```python
# 数据库连接池
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 0
}

# Redis连接池
REDIS_CONNECTION_POOL = {
    'max_connections': 50,
    'retry_on_timeout': True,
    'socket_keepalive': True,
    'socket_keepalive_options': {}
}
```

#### 缓存策略
```python
# 多级缓存
@cache.memoize(timeout=3600)  # Redis缓存1小时
def get_stock_info(stock_code):
    return db.session.query(Stock).filter_by(code=stock_code).first()

# CDN缓存配置
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## 容灾恢复

### 容灾目标
- **RTO (Recovery Time Objective)**: 4小时
- **RPO (Recovery Point Objective)**: 1小时
- **可用性目标**: 99.9%

### 容灾方案

#### 1. 数据中心级容灾
```
主数据中心 (US-West-1)
├── 所有服务正常运行
├── 实时数据备份到备用数据中心
└── 监控系统持续检查健康状态

备用数据中心 (US-East-1)  
├── 热备服务器待机
├── 数据库实时同步
├── 应用代码和配置同步
└── 接收健康检查信号
```

#### 2. 故障切换流程
```bash
#!/bin/bash
# failover.sh

# 1. 检测主数据中心故障
if ! curl -f https://api.equitycompass.com/health; then
    echo "主数据中心故障，开始切换"
    
    # 2. 激活备用数据中心
    ssh backup-dc "cd /opt/equitycompass && docker-compose up -d"
    
    # 3. 更新DNS记录
    aws route53 change-resource-record-sets \
        --hosted-zone-id Z123456789 \
        --change-batch file://failover-dns.json
    
    # 4. 通知相关人员
    curl -X POST $SLACK_WEBHOOK \
        -d '{"text":"紧急：已切换到备用数据中心"}'
fi
```

---

*此文档详细描述了智策股析项目的完整部署架构，从开发环境到生产环境的全方位部署指南。*
