#!/usr/bin/env python3
"""
生产环境部署脚本
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def check_environment():
    """检查环境配置"""
    print("🔍 检查生产环境配置...")
    
    # 注意：支付功能已移除，不再检查支付相关环境变量
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    
    print("✅ 环境变量检查通过")
    return True

def backup_database():
    """备份数据库"""
    print("📋 备份数据库...")
    
    db_file = Path("instance/production.db")
    if db_file.exists():
        backup_file = f"backups/production_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        shutil.copy2(db_file, backup_file)
        print(f"✅ 数据库已备份到: {backup_file}")
    else:
        print("ℹ️  数据库文件不存在，跳过备份")

def install_dependencies():
    """安装依赖"""
    print("📦 安装生产环境依赖...")
    
    try:
        # 注意：支付功能已移除，不再安装支付SDK
        # 所有依赖在requirements.txt中管理
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    
    return True

def run_migrations():
    """运行数据库迁移"""
    print("🗄️  运行数据库迁移...")
    
    try:
        # 创建金币系统表
        subprocess.run([sys.executable, "scripts/create_coin_tables.py"], check=True)
        print("✅ 数据库迁移完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False
    
    return True

def setup_ssl():
    """设置SSL证书"""
    print("🔒 设置SSL证书...")
    
    ssl_dir = Path("ssl")
    if not ssl_dir.exists():
        ssl_dir.mkdir()
        print("📁 创建SSL目录")
    
    # 检查SSL证书文件
    cert_file = ssl_dir / "cert.pem"
    key_file = ssl_dir / "key.pem"
    
    if not cert_file.exists() or not key_file.exists():
        print("⚠️  SSL证书文件不存在")
        print("请将SSL证书文件放置在 ssl/ 目录下：")
        print("  - ssl/cert.pem (证书文件)")
        print("  - ssl/key.pem (私钥文件)")
        return False
    
    print("✅ SSL证书检查通过")
    return True

def create_systemd_service():
    """创建systemd服务文件"""
    print("🔧 创建systemd服务...")
    
    service_content = f"""[Unit]
Description=EquityCompass Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={Path.cwd()}
Environment=PATH={Path.cwd()}/venv/bin
ExecStart={Path.cwd()}/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("/etc/systemd/system/equitycompass.service")
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        print("✅ systemd服务文件已创建")
        return True
    except PermissionError:
        print("⚠️  需要sudo权限创建systemd服务文件")
        print("请手动创建服务文件或使用sudo运行此脚本")
        return False

def start_services():
    """启动服务"""
    print("🚀 启动服务...")
    
    try:
        # 重新加载systemd
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        
        # 启动服务
        subprocess.run(["sudo", "systemctl", "start", "equitycompass"], check=True)
        
        # 设置开机自启
        subprocess.run(["sudo", "systemctl", "enable", "equitycompass"], check=True)
        
        print("✅ 服务启动成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务启动失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始生产环境部署...")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 备份数据库
    backup_database()
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 运行迁移
    if not run_migrations():
        sys.exit(1)
    
    # 设置SSL
    if not setup_ssl():
        print("⚠️  SSL设置失败，但继续部署")
    
    # 创建systemd服务
    if not create_systemd_service():
        print("⚠️  systemd服务创建失败，但继续部署")
    
    # 启动服务
    if not start_services():
        print("⚠️  服务启动失败，请手动启动")
    
    print("=" * 50)
    print("🎉 生产环境部署完成！")
    print("\n📋 后续步骤：")
    print("1. 检查服务状态: sudo systemctl status equitycompass")
    print("2. 查看日志: sudo journalctl -u equitycompass -f")
    print("3. 配置Nginx反向代理")
    print("4. 设置防火墙规则")
    print("5. 配置监控和告警")

if __name__ == "__main__":
    main()
