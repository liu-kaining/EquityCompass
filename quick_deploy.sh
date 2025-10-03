#!/bin/bash
# 快速部署脚本

set -e

echo "🚀 开始快速部署..."

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "❌ 请不要使用root用户运行此脚本"
    exit 1
fi

# 检查环境变量
if [ -z "$DOMAIN" ]; then
    echo "❌ 请设置DOMAIN环境变量"
    echo "例如: export DOMAIN=yourdomain.com"
    exit 1
fi

# 1. 安装依赖
echo "📦 安装系统依赖..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx

# 2. 创建应用目录
echo "📁 创建应用目录..."
sudo mkdir -p /opt/equitycompass
sudo chown $USER:$USER /opt/equitycompass

# 3. 克隆代码
echo "📥 克隆代码..."
cd /opt/equitycompass
git clone https://github.com/yourusername/EquityCompass.git .

# 4. 创建虚拟环境
echo "🐍 创建虚拟环境..."
cd backend
python3 -m venv venv
source venv/bin/activate

# 5. 安装Python依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt
pip install alipay-sdk-python stripe

# 6. 配置环境变量
echo "⚙️  配置环境变量..."
if [ ! -f .env ]; then
    cp production.env.example .env
    echo "请编辑 .env 文件设置支付配置"
    echo "按任意键继续..."
    read -n 1
fi

# 7. 运行数据库迁移
echo "🗄️  运行数据库迁移..."
python scripts/create_coin_tables.py

# 8. 配置Nginx
echo "🌐 配置Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/equitycompass
sudo sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/equitycompass
sudo ln -sf /etc/nginx/sites-available/equitycompass /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 9. 获取SSL证书
echo "🔒 获取SSL证书..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# 10. 创建systemd服务
echo "🔧 创建systemd服务..."
sudo tee /etc/systemd/system/equitycompass.service > /dev/null << EOF
[Unit]
Description=EquityCompass Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/equitycompass/backend
Environment=PATH=/opt/equitycompass/backend/venv/bin
ExecStart=/opt/equitycompass/backend/venv/bin/python run_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 11. 启动服务
echo "🚀 启动服务..."
sudo systemctl daemon-reload
sudo systemctl start equitycompass
sudo systemctl enable equitycompass
sudo systemctl restart nginx

# 12. 配置防火墙
echo "🔥 配置防火墙..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "🎉 部署完成！"
echo "访问地址: https://$DOMAIN"
echo "管理命令:"
echo "  查看状态: sudo systemctl status equitycompass"
echo "  查看日志: sudo journalctl -u equitycompass -f"
echo "  重启服务: sudo systemctl restart equitycompass"
