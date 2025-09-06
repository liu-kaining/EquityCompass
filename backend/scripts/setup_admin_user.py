#!/usr/bin/env python3
"""
为管理员邮箱创建用户账户
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.config.settings import DevelopmentConfig

def setup_admin_user():
    """为管理员邮箱创建用户账户"""
    app = create_app('development')
    
    with app.app_context():
        config = DevelopmentConfig()
        admin_username = config.ADMIN_USERNAME
        admin_email = config.ADMIN_EMAIL
        admin_password = config.ADMIN_PASSWORD
        admin_nickname = config.ADMIN_NICKNAME
        
        print(f"管理员用户名: {admin_username}")
        print(f"管理员邮箱: {admin_email}")
        print(f"管理员昵称: {admin_nickname}")
        
        user_repo = UserRepository(db.session)
        
        # 检查是否已存在该邮箱的用户
        existing_user = user_repo.get_by_email(admin_email)
        if existing_user:
            print(f"用户已存在: {existing_user.username}")
            print(f"当前角色: {existing_user.user_role}")
            
            # 更新为超级管理员角色
            if existing_user.user_role != 'SUPER_ADMIN':
                user_repo.update_user_role(existing_user.id, 'SUPER_ADMIN')
                print("✅ 已更新为超级管理员角色")
            else:
                print("✅ 已经是超级管理员")
            
            return existing_user
        
        # 创建新的管理员用户
        try:
            admin_user = user_repo.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                nickname=admin_nickname,
                user_role='SUPER_ADMIN'
            )
            
            print("✅ 管理员用户创建成功！")
            print(f"用户名: {admin_user.username}")
            print(f"密码: {admin_password}")
            print(f"邮箱: {admin_user.email}")
            print(f"角色: {admin_user.user_role}")
            print("\n⚠️  请及时修改默认密码！")
            
            return admin_user
            
        except Exception as e:
            print(f"❌ 创建管理员用户失败: {e}")
            return None

if __name__ == "__main__":
    print("正在为管理员邮箱创建用户账户...")
    admin = setup_admin_user()
    
    if admin:
        # 重新获取配置以显示密码
        from app.config.settings import DevelopmentConfig
        config = DevelopmentConfig()
        
        print("\n🎉 管理员用户账户创建完成！")
        print("\n登录信息：")
        print(f"用户名: {admin.username}")
        print(f"密码: {config.ADMIN_PASSWORD}")
        print(f"邮箱: {admin.email}")
        print("\n请在登录后及时修改密码！")
    else:
        print("\n❌ 管理员用户账户创建失败！")
