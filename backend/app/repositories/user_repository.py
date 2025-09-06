"""
用户数据访问层
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.base import SQLAlchemyRepository
from app.models.user import User


class UserRepository(SQLAlchemyRepository):
    """用户数据访问接口"""
    
    def __init__(self, session: Session):
        super().__init__(User, session)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.session.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.session.query(User).filter(User.username == username).first()
    
    def create_user(self, username: str, email: str, password: str, nickname: str = None, user_role: str = 'USER') -> User:
        """创建新用户"""
        user = User(
            username=username,
            email=email,
            nickname=nickname or username,
            plan_type='TRIAL',
            remaining_quota=1,
            user_role=user_role,
            is_active=True,
            email_verified=False
        )
        user.set_password(password)
        self.session.add(user)
        self.session.commit()
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户登录"""
        user = self.get_by_username(username)
        if user and user.check_password(password) and user.is_active:
            return user
        return None
    
    def update_quota(self, user_id: int, remaining_quota: int) -> Optional[User]:
        """更新用户剩余额度"""
        return self.update(user_id, {'remaining_quota': remaining_quota})
    
    def update_plan(self, user_id: int, plan_type: str, quota: int = None) -> Optional[User]:
        """更新用户计划"""
        update_data = {'plan_type': plan_type}
        if quota is not None:
            update_data['remaining_quota'] = quota
        return self.update(user_id, update_data)
    
    def get_active_users(self) -> List[User]:
        """获取活跃用户"""
        return self.get_all(is_active=True)
    
    def get_trial_users(self) -> List[User]:
        """获取试用用户"""
        return self.get_all(plan_type='TRIAL')
    
    def get_premium_users(self) -> List[User]:
        """获取付费用户"""
        return self.session.query(User).filter(
            User.plan_type.in_(['SUBSCRIPTION', 'PAY_PER_USE'])
        ).all()
    
    def get_all_users(self, page: int = 1, per_page: int = 20) -> List[User]:
        """获取所有用户（分页）"""
        offset = (page - 1) * per_page
        return self.session.query(User).offset(offset).limit(per_page).all()
    
    def get_users_by_role(self, role: str) -> List[User]:
        """根据角色获取用户"""
        return self.session.query(User).filter(User.user_role == role).all()
    
    def update_user_role(self, user_id: int, new_role: str) -> Optional[User]:
        """更新用户角色"""
        return self.update(user_id, {'user_role': new_role})
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """禁用用户"""
        return self.update(user_id, {'is_active': False})
    
    def activate_user(self, user_id: int) -> Optional[User]:
        """启用用户"""
        return self.update(user_id, {'is_active': True})
    
    def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        from sqlalchemy import func
        
        total_users = self.session.query(func.count(User.id)).scalar()
        active_users = self.session.query(func.count(User.id)).filter(User.is_active == True).scalar()
        super_admins = self.session.query(func.count(User.id)).filter(User.user_role == 'SUPER_ADMIN').scalar()
        site_admins = self.session.query(func.count(User.id)).filter(User.user_role == 'SITE_ADMIN').scalar()
        regular_users = self.session.query(func.count(User.id)).filter(User.user_role == 'USER').scalar()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'super_admins': super_admins,
            'site_admins': site_admins,
            'regular_users': regular_users
        }
