"""
用户数据访问层
"""
from typing import Optional, List
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
    
    def create_user(self, email: str, nickname: str = None) -> User:
        """创建新用户"""
        user_data = {
            'email': email,
            'nickname': nickname or email.split('@')[0],
            'plan_type': 'TRIAL',
            'remaining_quota': 1,
            'is_active': True
        }
        return self.create(user_data)
    
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
