#!/usr/bin/env python3
"""
初始化AI配置脚本
从环境变量导入AI配置到数据库
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.services.ai.ai_config_service import AIConfigService

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始初始化AI配置...")
        
        # 创建AI配置服务
        service = AIConfigService(db.session)
        
        # 从环境变量导入配置
        result = service.import_from_env()
        
        if result['success']:
            print(f"✅ 成功导入 {result['imported_count']} 个AI配置")
            
            # 显示导入的配置
            configs = service.get_all_configs()
            if configs:
                print("\n📋 当前AI配置列表:")
                for config in configs:
                    status = "✅ 激活" if config['is_active'] else "❌ 停用"
                    default = "⭐ 默认" if config['is_default'] else ""
                    print(f"  - {config['display_name']} ({config['provider_name']}) - {config['model_name']} {status} {default}")
            
            # 如果没有默认配置，设置第一个为默认
            default_config = service.get_default_config()
            if not default_config:
                configs = service.get_active_configs()
                if configs:
                    first_config = configs[0]
                    service.set_default_config(first_config['id'])
                    print(f"✅ 已设置 {first_config['display_name']} 为默认配置")
        else:
            print(f"❌ 导入失败: {result['error']}")
        
        print("\n🎉 AI配置初始化完成！")

if __name__ == "__main__":
    main()
