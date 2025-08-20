#!/bin/bash

# 智策股析 - 生产环境一键部署脚本
# 使用方法: ./setup_production.sh

set -e  # 遇到错误立即退出

echo "🚀 智策股析 - 生产环境部署脚本"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}错误: 请不要使用root用户运行此脚本${NC}"
   exit 1
fi

# 检查操作系统
OS=$(uname -s)
if [[ "$OS" == "Darwin" ]]; then
    echo -e "${YELLOW}检测到macOS系统${NC}"
    PACKAGE_MANAGER="brew"
elif [[ "$OS" == "Linux" ]]; then
    if command -v apt-get &> /dev/null; then
        echo -e "${YELLOW}检测到Ubuntu/Debian系统${NC}"
        PACKAGE_MANAGER="apt"
    elif command -v yum &> /dev/null; then
        echo -e "${YELLOW}检测到CentOS/RHEL系统${NC}"
        PACKAGE_MANAGER="yum"
    else
        echo -e "${RED}不支持的Linux发行版${NC}"
        exit 1
    fi
else
    echo -e "${RED}不支持的操作系统: $OS${NC}"
    exit 1
fi

# 项目配置
PROJECT_NAME="equitycompass"
PROJECT_DIR="/opt/$PROJECT_NAME"
SERVICE_USER="$PROJECT_NAME"
SERVICE_GROUP="$PROJECT_NAME"

echo -e "${BLUE}开始部署 $PROJECT_NAME 到生产环境...${NC}"

# 1. 创建系统用户
echo -e "${YELLOW}1. 创建系统用户...${NC}"
if ! id "$SERVICE_USER" &>/dev/null; then
    sudo useradd -r -s /bin/bash -d $PROJECT_DIR $SERVICE_USER
    echo -e "${GREEN}✓ 创建用户 $SERVICE_USER${NC}"
else
    echo -e "${GREEN}✓ 用户 $SERVICE_USER 已存在${NC}"
fi

# 2. 创建项目目录
echo -e "${YELLOW}2. 创建项目目录...${NC}"
sudo mkdir -p $PROJECT_DIR
sudo chown $SERVICE_USER:$SERVICE_GROUP $PROJECT_DIR
echo -e "${GREEN}✓ 项目目录创建完成${NC}"

# 3. 安装系统依赖
echo -e "${YELLOW}3. 安装系统依赖...${NC}"

if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv nginx redis-server postgresql postgresql-contrib curl wget git
elif [[ "$PACKAGE_MANAGER" == "yum" ]]; then
    sudo yum update -y
    sudo yum install -y python3 python3-pip nginx redis postgresql postgresql-server curl wget git
    sudo postgresql-setup initdb
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
elif [[ "$PACKAGE_MANAGER" == "brew" ]]; then
    brew install python3 nginx redis postgresql curl wget git
    brew services start postgresql
    brew services start redis
fi

echo -e "${GREEN}✓ 系统依赖安装完成${NC}"

# 4. 配置PostgreSQL
echo -e "${YELLOW}4. 配置PostgreSQL...${NC}"
if [[ "$PACKAGE_MANAGER" != "brew" ]]; then
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
fi

# 创建数据库和用户
sudo -u postgres psql -c "CREATE DATABASE $PROJECT_NAME;" 2>/dev/null || echo "数据库已存在"
sudo -u postgres psql -c "CREATE USER ${PROJECT_NAME}_user WITH PASSWORD '${PROJECT_NAME}_password';" 2>/dev/null || echo "用户已存在"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $PROJECT_NAME TO ${PROJECT_NAME}_user;" 2>/dev/null || echo "权限已设置"

echo -e "${GREEN}✓ PostgreSQL配置完成${NC}"

# 5. 配置Redis
echo -e "${YELLOW}5. 配置Redis...${NC}"
if [[ "$PACKAGE_MANAGER" != "brew" ]]; then
    sudo systemctl start redis
    sudo systemctl enable redis
fi

# 设置Redis密码
sudo sed -i 's/# requirepass foobared/requirepass equitycompass_redis_password/' /etc/redis/redis.conf 2>/dev/null || echo "Redis配置已更新"

echo -e "${GREEN}✓ Redis配置完成${NC}"

# 6. 复制项目文件
echo -e "${YELLOW}6. 复制项目文件...${NC}"
# 这里假设脚本在项目根目录运行
CURRENT_DIR=$(pwd)
sudo cp -r $CURRENT_DIR/* $PROJECT_DIR/
sudo chown -R $SERVICE_USER:$SERVICE_GROUP $PROJECT_DIR

echo -e "${GREEN}✓ 项目文件复制完成${NC}"

# 7. 创建Python虚拟环境
echo -e "${YELLOW}7. 创建Python虚拟环境...${NC}"
cd $PROJECT_DIR/backend
sudo -u $SERVICE_USER python3 -m venv venv
sudo -u $SERVICE_USER $PROJECT_DIR/backend/venv/bin/pip install --upgrade pip
sudo -u $SERVICE_USER $PROJECT_DIR/backend/venv/bin/pip install -r requirements.txt
sudo -u $SERVICE_USER $PROJECT_DIR/backend/venv/bin/pip install gunicorn psycopg2-binary

echo -e "${GREEN}✓ Python虚拟环境创建完成${NC}"

# 8. 创建环境变量文件
echo -e "${YELLOW}8. 创建环境变量文件...${NC}"
sudo tee $PROJECT_DIR/.env > /dev/null <<EOF
# 生产环境配置
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 数据库配置
DATABASE_URL=postgresql://${PROJECT_NAME}_user:${PROJECT_NAME}_password@localhost:5432/$PROJECT_NAME

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=equitycompass_redis_password

# 邮件配置 (需要手动配置)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=智策股析
SEND_EMAIL=true

# 其他配置
DEBUG=false
TESTING=false
EOF

sudo chown $SERVICE_USER:$SERVICE_GROUP $PROJECT_DIR/.env
echo -e "${GREEN}✓ 环境变量文件创建完成${NC}"

# 9. 创建Gunicorn配置文件
echo -e "${YELLOW}9. 创建Gunicorn配置...${NC}"
sudo tee $PROJECT_DIR/backend/gunicorn.conf.py > /dev/null <<EOF
bind = "127.0.0.1:5001"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
user = "$SERVICE_USER"
group = "$SERVICE_GROUP"
EOF

echo -e "${GREEN}✓ Gunicorn配置创建完成${NC}"

# 10. 创建系统服务
echo -e "${YELLOW}10. 创建系统服务...${NC}"
sudo tee /etc/systemd/system/$PROJECT_NAME.service > /dev/null <<EOF
[Unit]
Description=EquityCompass Flask Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$PROJECT_DIR/backend
Environment=PATH=$PROJECT_DIR/backend/venv/bin
Environment=FLASK_ENV=production
ExecStart=$PROJECT_DIR/backend/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $PROJECT_NAME
echo -e "${GREEN}✓ 系统服务创建完成${NC}"

# 11. 配置Nginx
echo -e "${YELLOW}11. 配置Nginx...${NC}"
sudo tee /etc/nginx/sites-available/$PROJECT_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location /static/ {
        alias $PROJECT_DIR/backend/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${GREEN}✓ Nginx配置完成${NC}"

# 12. 初始化数据库
echo -e "${YELLOW}12. 初始化数据库...${NC}"
cd $PROJECT_DIR/backend
sudo -u $SERVICE_USER $PROJECT_DIR/backend/venv/bin/python app.py init_db
echo -e "${GREEN}✓ 数据库初始化完成${NC}"

# 13. 启动服务
echo -e "${YELLOW}13. 启动服务...${NC}"
sudo systemctl start $PROJECT_NAME
sudo systemctl status $PROJECT_NAME --no-pager

echo -e "${GREEN}✓ 服务启动完成${NC}"

# 14. 创建备份脚本
echo -e "${YELLOW}14. 创建备份脚本...${NC}"
sudo tee /usr/local/bin/backup-$PROJECT_NAME.sh > /dev/null <<EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/$PROJECT_NAME"
mkdir -p \$BACKUP_DIR

# 数据库备份
pg_dump $PROJECT_NAME > \$BACKUP_DIR/${PROJECT_NAME}_db_\$DATE.sql
gzip \$BACKUP_DIR/${PROJECT_NAME}_db_\$DATE.sql

# 文件备份
tar -czf \$BACKUP_DIR/${PROJECT_NAME}_files_\$DATE.tar.gz -C $PROJECT_DIR/data .

# 保留最近30天的备份
find \$BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
EOF

sudo chmod +x /usr/local/bin/backup-$PROJECT_NAME.sh
echo -e "${GREEN}✓ 备份脚本创建完成${NC}"

# 15. 创建健康检查脚本
echo -e "${YELLOW}15. 创建健康检查脚本...${NC}"
sudo tee /usr/local/bin/health-check-$PROJECT_NAME.sh > /dev/null <<EOF
#!/bin/bash
curl -f http://localhost:5001/api/health || exit 1
EOF

sudo chmod +x /usr/local/bin/health-check-$PROJECT_NAME.sh
echo -e "${GREEN}✓ 健康检查脚本创建完成${NC}"

# 16. 设置定时任务
echo -e "${YELLOW}16. 设置定时任务...${NC}"
# 每天凌晨2点备份
echo "0 2 * * * /usr/local/bin/backup-$PROJECT_NAME.sh" | sudo crontab -

echo -e "${GREEN}✓ 定时任务设置完成${NC}"

# 17. 配置防火墙
echo -e "${YELLOW}17. 配置防火墙...${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
    echo -e "${GREEN}✓ 防火墙配置完成${NC}"
else
    echo -e "${YELLOW}⚠ UFW未安装，跳过防火墙配置${NC}"
fi

# 18. 最终检查
echo -e "${YELLOW}18. 最终检查...${NC}"
sleep 5

# 检查服务状态
if sudo systemctl is-active --quiet $PROJECT_NAME; then
    echo -e "${GREEN}✓ $PROJECT_NAME 服务运行正常${NC}"
else
    echo -e "${RED}✗ $PROJECT_NAME 服务启动失败${NC}"
    sudo systemctl status $PROJECT_NAME --no-pager
fi

# 检查健康状态
if curl -f http://localhost:5001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 应用健康检查通过${NC}"
else
    echo -e "${RED}✗ 应用健康检查失败${NC}"
fi

echo ""
echo -e "${GREEN}🎉 智策股析生产环境部署完成！${NC}"
echo "=================================="
echo -e "${BLUE}重要信息：${NC}"
echo "• 项目目录: $PROJECT_DIR"
echo "• 服务用户: $SERVICE_USER"
echo "• 数据库: $PROJECT_NAME"
echo "• 服务端口: 5001"
echo "• Nginx端口: 80"
echo ""
echo -e "${YELLOW}⚠️  需要手动配置：${NC}"
echo "1. 编辑 $PROJECT_DIR/.env 文件，配置邮件服务"
echo "2. 配置域名和SSL证书"
echo "3. 配置LLM API密钥"
echo "4. 配置支付网关"
echo ""
echo -e "${BLUE}常用命令：${NC}"
echo "• 查看服务状态: sudo systemctl status $PROJECT_NAME"
echo "• 重启服务: sudo systemctl restart $PROJECT_NAME"
echo "• 查看日志: sudo journalctl -u $PROJECT_NAME -f"
echo "• 手动备份: /usr/local/bin/backup-$PROJECT_NAME.sh"
echo "• 健康检查: /usr/local/bin/health-check-$PROJECT_NAME.sh"
echo ""
echo -e "${GREEN}部署完成！请访问 http://yourdomain.com 查看应用${NC}"
