#!/usr/bin/env python3
"""
项目健康检查脚本
验证整理后的代码结构是否正常工作
"""
import sys
import os
import subprocess

def check_python_environment():
    """检查Python环境"""
    print("🐍 检查Python环境...")
    try:
        import flask
        import sqlalchemy
        import redis
        print("    ✅ 核心依赖库正常")
        return True
    except ImportError as e:
        print(f"    ❌ 依赖库缺失: {e}")
        return False

def check_database():
    """检查数据库连接"""
    print("🗃️ 检查数据库...")
    try:
        from app import create_app, db
        app = create_app('development')
        
        with app.app_context():
            # 检查数据库连接
            result = db.session.execute('SELECT 1').scalar()
            if result == 1:
                print("    ✅ 数据库连接正常")
                return True
    except Exception as e:
        print(f"    ❌ 数据库连接失败: {e}")
        return False

def check_services():
    """检查核心服务"""
    print("🔧 检查核心服务...")
    try:
        from app.services.auth.jwt_service import JWTService
        from app.services.auth.verification_code_service import VerificationCodeService
        from app.services.email.email_service import EmailService
        
        # 简单实例化测试
        jwt_service = JWTService()
        verification_service = VerificationCodeService()
        email_service = EmailService()
        
        print("    ✅ 认证服务正常")
        print("    ✅ 验证码服务正常")
        print("    ✅ 邮件服务正常")
        return True
    except Exception as e:
        print(f"    ❌ 服务加载失败: {e}")
        return False

def check_repositories():
    """检查Repository层"""
    print("🏪 检查Repository层...")
    try:
        from app import create_app, db
        from app.repositories.user_repository import UserRepository
        from app.repositories.stock_repository import StockRepository
        
        app = create_app('development')
        with app.app_context():
            user_repo = UserRepository(db.session)
            stock_repo = StockRepository(db.session)
            
            # 检查基本功能
            stock_count = stock_repo.count()
            print(f"    ✅ 股票数据: {stock_count} 支")
            print("    ✅ Repository层正常")
            return True
    except Exception as e:
        print(f"    ❌ Repository层错误: {e}")
        return False

def check_api_endpoints():
    """检查API端点"""
    print("🌐 检查API端点...")
    try:
        from app import create_app
        app = create_app('development')
        
        with app.test_client() as client:
            # 检查健康检查端点
            response = client.get('/api/health')
            if response.status_code == 200:
                print("    ✅ 健康检查API正常")
                
                # 检查登录页面
                response = client.get('/auth/login')
                if response.status_code == 200:
                    print("    ✅ 登录页面正常")
                    return True
    except Exception as e:
        print(f"    ❌ API端点错误: {e}")
        return False

def run_health_check():
    """运行完整健康检查"""
    print("🏥 智策股析项目健康检查\n")
    
    checks = [
        check_python_environment,
        check_database,
        check_services,
        check_repositories,
        check_api_endpoints
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        try:
            if check():
                passed += 1
            print()  # 空行分隔
        except Exception as e:
            print(f"    ❌ 检查过程出错: {e}\n")
    
    # 结果总结
    print("=" * 50)
    print("📋 健康检查总结")
    print("=" * 50)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {total - passed}")
    print(f"📊 总计: {total}")
    
    success_rate = (passed / total) * 100
    print(f"📈 成功率: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 恭喜！项目健康状况良好，所有核心功能正常！")
        print("🚀 可以继续开发或启动应用服务")
        return True
    else:
        print(f"\n⚠️ 发现 {total - passed} 个问题，建议修复后再继续")
        print("🔧 请检查环境配置和依赖安装")
        return False

if __name__ == '__main__':
    success = run_health_check()
    sys.exit(0 if success else 1)
