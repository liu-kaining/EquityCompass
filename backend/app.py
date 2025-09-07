#!/usr/bin/env python3
"""
智策股析 - 应用启动脚本
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def main():
    """启动应用"""
    # 从环境变量获取配置
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    # 获取端口号
    port = int(os.environ.get('PORT', 5002))
    
    print(f"🚀 启动智策股析应用...")
    print(f"📡 服务地址: http://localhost:{port}")
    print(f"🔧 环境: {config_name}")
    print(f"📊 统计功能: 已启用")
    
    # 启动应用
    app.run(
        host='0.0.0.0',
        port=port,
        debug=(config_name == 'development'),
        threaded=True
    )

if __name__ == '__main__':
    main()
