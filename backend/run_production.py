#!/usr/bin/env python3
"""
生产环境启动脚本
"""
import os
import sys
from pathlib import Path

# 设置生产环境
os.environ['ENV'] = 'production'
os.environ['FLASK_ENV'] = 'production'

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix

def create_production_app():
    """创建生产环境应用"""
    app = create_app()
    
    # 添加代理中间件（用于Nginx反向代理）
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    return app

def main():
    """主函数"""
    print("🚀 启动生产环境...")
    
    # 检查环境变量
    required_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # 创建应用
    app = create_production_app()
    
    # 获取配置
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5002))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"📡 服务地址: http://{host}:{port}")
    print(f"🔧 环境: production")
    print(f"🐛 调试模式: {'开启' if debug else '关闭'}")
    
    # 启动服务
    try:
        run_simple(
            hostname=host,
            port=port,
            application=app,
            use_reloader=debug,
            use_debugger=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
