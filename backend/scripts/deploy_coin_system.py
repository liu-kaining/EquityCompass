#!/usr/bin/env python3
"""
金币系统生产环境部署脚本
用于在生产环境中安全部署金币系统

使用方法：
python scripts/deploy_coin_system.py [--environment production] [--maintenance-mode]
"""

import os
import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CoinSystemDeployment:
    def __init__(self, environment='production', maintenance_mode=False):
        self.environment = environment
        self.maintenance_mode = maintenance_mode
        self.deployment_log = []
        
    def log(self, message):
        """记录部署日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.deployment_log.append(log_message)
    
    def check_prerequisites(self):
        """检查部署前置条件"""
        self.log("检查部署前置条件...")
        
        # 检查数据库文件
        db_path = Path("instance/equitycompass.db")
        if not db_path.exists():
            self.log("❌ 数据库文件不存在")
            return False
            
        # 检查备份目录
        backup_dir = Path("backups")
        if not backup_dir.exists():
            backup_dir.mkdir()
            self.log("创建备份目录")
            
        # 检查Python环境
        try:
            import flask
            import sqlalchemy
            self.log("✅ Python环境检查通过")
        except ImportError as e:
            self.log(f"❌ Python环境检查失败: {e}")
            return False
            
        return True
    
    def create_maintenance_page(self):
        """创建维护页面"""
        if not self.maintenance_mode:
            return
            
        self.log("创建维护页面...")
        
        maintenance_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>系统维护中 - 智策股析</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .maintenance-container {
            background: white;
            padding: 3rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }
        .maintenance-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
        }
        p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #f0f0f0;
            border-radius: 2px;
            overflow: hidden;
            margin: 2rem 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            animation: progress 2s ease-in-out infinite;
        }
        @keyframes progress {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="maintenance-container">
        <div class="maintenance-icon">🔧</div>
        <h1>系统维护中</h1>
        <p>我们正在升级系统，为您带来更好的体验。</p>
        <p>预计维护时间：5-10分钟</p>
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        <p>请稍后再试，感谢您的耐心等待！</p>
    </div>
    
    <script>
        // 自动刷新页面
        setTimeout(function() {
            location.reload();
        }, 30000); // 30秒后自动刷新
    </script>
</body>
</html>
        """
        
        with open("maintenance.html", "w", encoding="utf-8") as f:
            f.write(maintenance_html)
            
        self.log("✅ 维护页面已创建")
    
    def stop_application(self):
        """停止应用"""
        self.log("停止应用服务...")
        
        try:
            # 查找并停止Flask应用进程
            result = subprocess.run(['pgrep', '-f', 'python.*app.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-TERM', pid])
                        self.log(f"停止进程 {pid}")
                        time.sleep(2)
            
            self.log("✅ 应用服务已停止")
        except Exception as e:
            self.log(f"停止应用时发生错误: {e}")
    
    def backup_database(self):
        """备份数据库"""
        self.log("备份数据库...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/pre_deployment_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2("instance/equitycompass.db", backup_file)
            self.log(f"✅ 数据库已备份: {backup_file}")
            return backup_file
        except Exception as e:
            self.log(f"❌ 数据库备份失败: {e}")
            raise
    
    def run_migration(self):
        """运行数据迁移"""
        self.log("运行数据迁移...")
        
        try:
            # 创建金币系统表
            result = subprocess.run([sys.executable, "scripts/create_coin_tables.py"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.log(f"❌ 创建表失败: {result.stderr}")
                raise Exception("创建表失败")
            
            # 运行数据迁移
            result = subprocess.run([sys.executable, "scripts/migrate_to_coin_system.py"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.log(f"❌ 数据迁移失败: {result.stderr}")
                raise Exception("数据迁移失败")
            
            self.log("✅ 数据迁移完成")
        except Exception as e:
            self.log(f"❌ 迁移过程中发生错误: {e}")
            raise
    
    def start_application(self):
        """启动应用"""
        self.log("启动应用服务...")
        
        try:
            # 启动Flask应用
            if self.environment == 'production':
                # 生产环境使用gunicorn
                subprocess.Popen(['gunicorn', '-w', '4', '-b', '0.0.0.0:5002', 'app:app'])
            else:
                # 开发环境使用Flask开发服务器
                subprocess.Popen([sys.executable, 'app.py'])
            
            time.sleep(5)  # 等待应用启动
            
            # 检查应用是否正常启动
            import requests
            try:
                response = requests.get('http://localhost:5002/api/health', timeout=10)
                if response.status_code == 200:
                    self.log("✅ 应用服务已启动")
                else:
                    self.log("❌ 应用启动异常")
            except Exception as e:
                self.log(f"❌ 应用健康检查失败: {e}")
                
        except Exception as e:
            self.log(f"❌ 启动应用时发生错误: {e}")
            raise
    
    def verify_deployment(self):
        """验证部署结果"""
        self.log("验证部署结果...")
        
        try:
            import requests
            
            # 检查健康状态
            response = requests.get('http://localhost:5002/api/health', timeout=10)
            if response.status_code != 200:
                self.log("❌ 健康检查失败")
                return False
            
            # 检查金币系统API
            response = requests.get('http://localhost:5002/api/coin/packages', timeout=10)
            if response.status_code != 200:
                self.log("❌ 金币系统API检查失败")
                return False
            
            self.log("✅ 部署验证通过")
            return True
            
        except Exception as e:
            self.log(f"❌ 部署验证失败: {e}")
            return False
    
    def cleanup_maintenance_files(self):
        """清理维护文件"""
        if self.maintenance_mode:
            try:
                if Path("maintenance.html").exists():
                    Path("maintenance.html").unlink()
                    self.log("✅ 维护页面已清理")
            except Exception as e:
                self.log(f"清理维护文件时发生错误: {e}")
    
    def save_deployment_log(self):
        """保存部署日志"""
        log_file = Path("deployment_logs") / f"coin_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("金币系统部署日志\n")
            f.write("=" * 50 + "\n")
            for log_entry in self.deployment_log:
                f.write(log_entry + "\n")
        
        self.log(f"部署日志已保存: {log_file}")
    
    def run_deployment(self):
        """执行完整部署流程"""
        self.log("开始金币系统部署...")
        self.log(f"环境: {self.environment}")
        self.log(f"维护模式: {self.maintenance_mode}")
        
        try:
            # 1. 检查前置条件
            if not self.check_prerequisites():
                raise Exception("前置条件检查失败")
            
            # 2. 创建维护页面
            self.create_maintenance_page()
            
            # 3. 停止应用
            self.stop_application()
            
            # 4. 备份数据库
            backup_file = self.backup_database()
            
            # 5. 运行迁移
            self.run_migration()
            
            # 6. 启动应用
            self.start_application()
            
            # 7. 验证部署
            if not self.verify_deployment():
                raise Exception("部署验证失败")
            
            # 8. 清理维护文件
            self.cleanup_maintenance_files()
            
            # 9. 保存日志
            self.save_deployment_log()
            
            self.log("✅ 金币系统部署完成！")
            self.log(f"备份文件: {backup_file}")
            
        except Exception as e:
            self.log(f"❌ 部署过程中发生错误: {str(e)}")
            self.log("请检查日志并手动回滚")
            raise


def main():
    parser = argparse.ArgumentParser(description='金币系统生产环境部署脚本')
    parser.add_argument('--environment', default='production', 
                       choices=['development', 'production'],
                       help='部署环境')
    parser.add_argument('--maintenance-mode', action='store_true',
                       help='启用维护模式')
    
    args = parser.parse_args()
    
    deployment = CoinSystemDeployment(
        environment=args.environment,
        maintenance_mode=args.maintenance_mode
    )
    
    deployment.run_deployment()


if __name__ == '__main__':
    main()
