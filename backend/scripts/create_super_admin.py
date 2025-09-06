#!/usr/bin/env python3
"""
创建超级管理员账户脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.repositories.user_repository import UserRepository

def create_super_admin():
    """创建超级管理员账户"""
    app = create_app('development')
    
    with app.app_context():
        user_repo = UserRepository(db.session)
        
        # 检查是否已存在超级管理员
        existing_admin = user_repo.get_by_username('admin')
        if existing_admin:
            print(f"超级管理员已存在: {existing_admin.username}")
            print(f"当前角色: {existing_admin.user_role}")
            
            # 更新为超级管理员角色
            if existing_admin.user_role != 'SUPER_ADMIN':
                user_repo.update_user_role(existing_admin.id, 'SUPER_ADMIN')
                print("✅ 已更新为超级管理员角色")
            else:
                print("✅ 已经是超级管理员")
            
            return existing_admin
        
        # 创建新的超级管理员
        try:
            admin_user = user_repo.create_user(
                username='admin',
                email='admin@equitycompass.com',
                password='admin123456',  # 默认密码
                nickname='系统管理员',
                user_role='SUPER_ADMIN'
            )
            
            print("✅ 超级管理员创建成功！")
            print(f"用户名: {admin_user.username}")
            print(f"密码: admin123456")
            print(f"邮箱: {admin_user.email}")
            print(f"角色: {admin_user.user_role}")
            print("\n⚠️  请及时修改默认密码！")
            
            return admin_user
            
        except Exception as e:
            print(f"❌ 创建超级管理员失败: {e}")
            return None

if __name__ == "__main__":
    print("正在创建超级管理员账户...")
    admin = create_super_admin()
    
    if admin:
        print("\n🎉 超级管理员账户创建完成！")
        print("\n登录信息：")
        print("用户名: admin")
        print("密码: admin123456")
        print("\n请在登录后及时修改密码！")
    else:
        print("\n❌ 超级管理员账户创建失败！")
