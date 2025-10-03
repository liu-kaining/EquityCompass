# 🚀 生产环境部署指南

## 📋 部署前准备

### 1. 服务器要求
- **操作系统**: Ubuntu 20.04+ 或 CentOS 8+
- **内存**: 最少 2GB，推荐 4GB+
- **存储**: 最少 20GB，推荐 50GB+
- **网络**: 公网IP，开放80/443端口

### 2. 域名和SSL证书
- 购买域名并解析到服务器IP
- 申请SSL证书（推荐Let's Encrypt免费证书）

## 🔧 服务器环境配置

### 1. 更新系统
```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y

# CentOS
sudo yum update -y
```

### 2. 安装必要软件
```bash
# Ubuntu
sudo apt install -y python3 python3-pip python3-venv nginx git

# CentOS
sudo yum install -y python3 python3-pip nginx git
```

### 3. 创建应用用户
```bash
sudo useradd -m -s /bin/bash equitycompass
sudo usermod -aG sudo equitycompass
```

## 💳 支付平台配置

### 1. 支付宝配置
参考 [支付宝配置指南](ALIPAY_SETUP_GUIDE.md)

### 2. 微信支付配置
参考 [微信支付配置指南](WECHAT_PAY_SETUP_GUIDE.md)

### 3. Stripe配置
参考 [Stripe配置指南](STRIPE_SETUP_GUIDE.md)

## 🚀 应用部署

### 1. 克隆代码
```bash
sudo -u equitycompass git clone https://github.com/yourusername/EquityCompass.git
cd EquityCompass/backend
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 安装支付SDK
```bash
pip install alipay-sdk-python stripe
```

### 4. 配置环境变量
```bash
# 复制配置模板
cp production.env.example .env

# 编辑配置文件
nano .env
```

### 5. 运行数据库迁移
```bash
python scripts/create_coin_tables.py
python scripts/migrate_to_coin_system.py
```

### 6. 测试应用
```bash
python run_production.py
```

## 🌐 Nginx配置

### 1. 配置Nginx
```bash
# 复制配置文件
sudo cp nginx.conf /etc/nginx/sites-available/equitycompass

# 创建软链接
sudo ln -s /etc/nginx/sites-available/equitycompass /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 2. 配置SSL证书
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔄 服务管理

### 1. 创建systemd服务
```bash
sudo python scripts/deploy_production.py
```

### 2. 管理服务
```bash
# 启动服务
sudo systemctl start equitycompass

# 停止服务
sudo systemctl stop equitycompass

# 重启服务
sudo systemctl restart equitycompass

# 查看状态
sudo systemctl status equitycompass

# 查看日志
sudo journalctl -u equitycompass -f
```

### 3. 设置开机自启
```bash
sudo systemctl enable equitycompass
sudo systemctl enable nginx
```

## 🔒 安全配置

### 1. 防火墙配置
```bash
# Ubuntu (ufw)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. 数据库安全
```bash
# 设置数据库文件权限
sudo chown equitycompass:equitycompass instance/production.db
sudo chmod 600 instance/production.db
```

### 3. 应用安全
```bash
# 设置应用目录权限
sudo chown -R equitycompass:equitycompass /path/to/EquityCompass
sudo chmod -R 755 /path/to/EquityCompass
```

## 📊 监控和日志

### 1. 日志配置
```bash
# 创建日志目录
sudo mkdir -p /var/log/equitycompass
sudo chown equitycompass:equitycompass /var/log/equitycompass

# 配置日志轮转
sudo nano /etc/logrotate.d/equitycompass
```

### 2. 监控配置
```bash
# 安装监控工具
sudo apt install htop iotop nethogs

# 配置系统监控
sudo apt install prometheus-node-exporter
```

## 🔄 更新和维护

### 1. 应用更新
```bash
# 备份数据库
python scripts/clear_all_data.py --backup

# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 运行迁移
python scripts/migrate_to_coin_system.py

# 重启服务
sudo systemctl restart equitycompass
```

### 2. 数据库备份
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp instance/production.db backups/production_backup_$DATE.db
find backups/ -name "*.db" -mtime +7 -delete
EOF

chmod +x backup.sh

# 设置定时备份
crontab -e
# 添加: 0 2 * * * /path/to/backup.sh
```

## 🚨 故障排除

### 1. 常见问题
- **服务无法启动**: 检查环境变量和端口占用
- **支付回调失败**: 检查Nginx配置和SSL证书
- **数据库错误**: 检查文件权限和磁盘空间

### 2. 日志查看
```bash
# 应用日志
sudo journalctl -u equitycompass -f

# Nginx日志
sudo tail -f /var/log/nginx/equitycompass_error.log

# 系统日志
sudo tail -f /var/log/syslog
```

### 3. 性能优化
```bash
# 数据库优化
sqlite3 instance/production.db "VACUUM;"

# 清理日志
sudo journalctl --vacuum-time=7d
```

## 📞 技术支持

如有问题，请：
1. 查看日志文件
2. 检查配置文件
3. 联系技术支持

---

**注意**: 生产环境部署前请务必在测试环境充分测试所有功能！
