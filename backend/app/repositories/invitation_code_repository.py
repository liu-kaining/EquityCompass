"""
邀请码仓库层
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
from datetime import datetime

from app.models.invitation_code import InvitationCode
from app.repositories.base import SQLAlchemyRepository


class InvitationCodeRepository(SQLAlchemyRepository):
    """邀请码仓库"""
    
    def __init__(self, db_session: Session):
        super().__init__(InvitationCode, db_session)
    
    def get_by_code(self, code: str) -> Optional[InvitationCode]:
        """
        根据邀请码内容获取
        
        Args:
            code: 邀请码（会自动标准化）
            
        Returns:
            InvitationCode对象或None
        """
        from app.models.invitation_code import InvitationCode as Model
        normalized_code = Model.normalize_code(code)
        if not normalized_code:
            return None
        
        return self.session.query(Model).filter(Model.code == normalized_code).first()
    
    def create_code(self, code: str, code_type: str, created_by: int) -> InvitationCode:
        """
        创建邀请码
        
        Args:
            code: 邀请码内容（会自动标准化）
            code_type: 码类型（INVITATION/RECHARGE）
            created_by: 创建者ID
            
        Returns:
            创建的InvitationCode对象
        """
        from app.models.invitation_code import InvitationCode as Model
        normalized_code = Model.normalize_code(code)
        
        invitation_code = Model(
            code=normalized_code,
            code_type=code_type,
            created_by=created_by,
            is_used=False
        )
        self.session.add(invitation_code)
        return invitation_code
    
    def mark_as_used(self, code_id: int, used_by: int) -> bool:
        """
        标记邀请码为已使用
        
        Args:
            code_id: 邀请码ID
            used_by: 使用者ID
            
        Returns:
            是否成功
        """
        code = self.get_by_id(code_id)
        if not code:
            return False
        
        if code.is_used:
            return False  # 已经被使用过了
        
        code.is_used = True
        code.used_by = used_by
        code.used_at = datetime.utcnow()
        return True
    
    def get_unused_codes(self, code_type: str = 'INVITATION', limit: Optional[int] = None) -> List[InvitationCode]:
        """
        获取未使用的邀请码列表
        
        Args:
            code_type: 码类型
            limit: 限制数量
            
        Returns:
            未使用的邀请码列表
        """
        query = self.session.query(InvitationCode).filter(
            and_(
                InvitationCode.code_type == code_type,
                InvitationCode.is_used == False
            )
        ).order_by(desc(InvitationCode.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_all_codes(self, code_type: str = 'INVITATION', status: Optional[str] = None, 
                     page: int = 1, per_page: int = 20) -> Dict:
        """
        获取所有邀请码（分页）
        
        Args:
            code_type: 码类型
            status: 状态筛选（all/used/unused）
            page: 页码
            per_page: 每页数量
            
        Returns:
            包含codes和pagination的字典
        """
        query = self.session.query(InvitationCode).filter(
            InvitationCode.code_type == code_type
        )
        
        # 状态筛选
        if status == 'used':
            query = query.filter(InvitationCode.is_used == True)
        elif status == 'unused':
            query = query.filter(InvitationCode.is_used == False)
        
        # 总数
        total = query.count()
        
        # 分页
        query = query.order_by(desc(InvitationCode.created_at))
        offset = (page - 1) * per_page
        codes = query.offset(offset).limit(per_page).all()
        
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'codes': codes,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages
            }
        }
    
    def get_codes_by_creator(self, creator_id: int, code_type: str = 'INVITATION') -> List[InvitationCode]:
        """
        获取指定创建者生成的所有邀请码
        
        Args:
            creator_id: 创建者ID
            code_type: 码类型
            
        Returns:
            邀请码列表
        """
        return self.session.query(InvitationCode).filter(
            and_(
                InvitationCode.created_by == creator_id,
                InvitationCode.code_type == code_type
            )
        ).order_by(desc(InvitationCode.created_at)).all()
    
    def get_statistics(self, code_type: str = 'INVITATION') -> Dict:
        """
        获取邀请码统计信息
        
        Args:
            code_type: 码类型
            
        Returns:
            统计信息字典
        """
        from sqlalchemy import func
        
        total = self.session.query(func.count(InvitationCode.id)).filter(
            InvitationCode.code_type == code_type
        ).scalar()
        
        used = self.session.query(func.count(InvitationCode.id)).filter(
            and_(
                InvitationCode.code_type == code_type,
                InvitationCode.is_used == True
            )
        ).scalar()
        
        unused = total - used
        
        return {
            'total': total or 0,
            'used': used or 0,
            'unused': unused or 0,
            'usage_rate': (used / total * 100) if total > 0 else 0
        }

