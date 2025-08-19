"""
用户数据服务
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.models.user import User


class UserDataService:
    """用户数据服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
    
    def authenticate_or_create_user(self, email: str) -> User:
        """认证或创建用户（邮箱验证码登录）"""
        user = self.user_repo.get_by_email(email)
        
        if not user:
            # 新用户自动创建
            nickname = email.split('@')[0]
            user = self.user_repo.create_user(email, nickname)
        
        return user
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户资料"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        return {
            'id': user.id,
            'email': user.email,
            'nickname': user.nickname,
            'plan_type': user.plan_type,
            'remaining_quota': user.remaining_quota,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    
    def update_user_profile(self, user_id: int, **updates) -> Optional[User]:
        """更新用户资料"""
        allowed_fields = ['nickname']
        update_data = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if update_data:
            return self.user_repo.update(user_id, update_data)
        return None
    
    def consume_quota(self, user_id: int, amount: int = 1) -> bool:
        """消费用户额度"""
        user = self.user_repo.get_by_id(user_id)
        if not user or user.remaining_quota < amount:
            return False
        
        new_quota = user.remaining_quota - amount
        self.user_repo.update_quota(user_id, new_quota)
        return True
    
    def add_quota(self, user_id: int, amount: int) -> Optional[User]:
        """增加用户额度"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        new_quota = user.remaining_quota + amount
        return self.user_repo.update_quota(user_id, new_quota)
    
    def upgrade_plan(self, user_id: int, plan_type: str, quota: int = None) -> Optional[User]:
        """升级用户计划"""
        plan_quotas = {
            'TRIAL': 1,
            'FREE': 5,
            'SUBSCRIPTION': 999,  # 无限制用999表示
            'PAY_PER_USE': quota or 0
        }
        
        if plan_type not in plan_quotas:
            raise ValueError(f"无效的计划类型: {plan_type}")
        
        final_quota = quota if quota is not None else plan_quotas[plan_type]
        return self.user_repo.update_plan(user_id, plan_type, final_quota)
    
    def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        total_users = self.user_repo.count()
        active_users = len(self.user_repo.get_active_users())
        trial_users = len(self.user_repo.get_trial_users())
        premium_users = len(self.user_repo.get_premium_users())
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'trial_users': trial_users,
            'premium_users': premium_users,
            'conversion_rate': premium_users / total_users if total_users > 0 else 0
        }
