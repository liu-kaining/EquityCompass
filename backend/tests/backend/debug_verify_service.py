#!/usr/bin/env python3
"""
调试验证服务
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.auth.verification_code_service import VerificationCodeService
from app.services.data.user_service import UserDataService
from app.services.auth.jwt_service import JWTService

def debug_verification_flow():
    """调试验证流程"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # 初始化数据库
            db.create_all()
            print("✅ 数据库初始化成功")
            
            # 测试验证码服务
            email = "debug@test.com"
            verification_service = VerificationCodeService()
            
            print(f"\n📧 为 {email} 生成验证码...")
            result = verification_service.send_code(email)
            print(f"结果: {result}")
            
            if result['success']:
                code = result['data']['code']
                print(f"验证码: {code}")
                
                # 验证验证码
                print(f"\n🔐 验证验证码...")
                verify_result = verification_service.verify_code(email, code)
                print(f"验证结果: {verify_result}")
                
                if verify_result['success']:
                    # 测试用户服务
                    print(f"\n👤 测试用户服务...")
                    user_service = UserDataService(db.session)
                    
                    user = user_service.authenticate_or_create_user(email)
                    print(f"用户创建/获取: {user}")
                    print(f"用户ID: {user.id}, 邮箱: {user.email}")
                    
                    # 测试JWT服务
                    print(f"\n🎫 测试JWT服务...")
                    jwt_service = JWTService()
                    
                    token_result = jwt_service.generate_token(
                        user_id=user.id,
                        email=user.email,
                        is_admin=False
                    )
                    print(f"Token生成结果: {token_result}")
                    
                    if token_result['success']:
                        access_token = token_result['data']['access_token']
                        print(f"✅ 完整流程测试成功！")
                        print(f"Token: {access_token[:50]}...")
                    else:
                        print(f"❌ Token生成失败")
                else:
                    print(f"❌ 验证码验证失败")
            else:
                print(f"❌ 验证码生成失败")
                
        except Exception as e:
            print(f"❌ 调试过程中出错: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_verification_flow()
