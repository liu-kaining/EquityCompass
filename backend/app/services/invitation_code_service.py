"""
邀请码服务层
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.invitation_code import InvitationCode
from app.repositories.invitation_code_repository import InvitationCodeRepository
from app.utils.code_generator import generate_invitation_code, generate_invitation_codes
from app.utils.response import service_success_response, service_error_response


class InvitationCodeService:
    """邀请码服务"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.repository = InvitationCodeRepository(db_session)
    
    def generate_code(self, created_by: int, code_type: str = 'INVITATION') -> Dict:
        """
        生成单个邀请码
        
        Args:
            created_by: 创建者ID（管理员）
            code_type: 码类型，默认INVITATION
            
        Returns:
            生成结果
        """
        try:
            # 生成邀请码，确保唯一性
            max_attempts = 10  # 最多尝试10次
            for _ in range(max_attempts):
                code = generate_invitation_code()
                
                # 检查是否已存在
                existing = self.repository.get_by_code(code)
                if not existing:
                    # 创建邀请码
                    invitation_code = self.repository.create_code(
                        code=code,
                        code_type=code_type,
                        created_by=created_by
                    )
                    self.db.commit()
                    
                    return service_success_response({
                        'id': invitation_code.id,
                        'code': invitation_code.code,
                        'code_display': invitation_code.format_display(),
                        'created_at': invitation_code.created_at.isoformat()
                    })
            
            return service_error_response("GENERATION_FAILED", "生成邀请码失败，请重试")
            
        except Exception as e:
            self.db.rollback()
            return service_error_response("GENERATION_ERROR", f"生成邀请码时发生错误: {str(e)}")
    
    def generate_codes_batch(self, created_by: int, count: int, code_type: str = 'INVITATION') -> Dict:
        """
        批量生成邀请码
        
        Args:
            created_by: 创建者ID（管理员）
            count: 生成数量（1-10）
            code_type: 码类型，默认INVITATION
            
        Returns:
            生成结果
        """
        try:
            # 验证数量
            if count < 1 or count > 10:
                return service_error_response("INVALID_COUNT", "批量生成数量必须在1-10之间")
            
            codes = []
            failed_count = 0
            max_attempts_per_code = 10
            
            for i in range(count):
                success = False
                for attempt in range(max_attempts_per_code):
                    code = generate_invitation_code()
                    
                    # 检查是否已存在（包括本次批量生成中已生成的）
                    existing = self.repository.get_by_code(code)
                    if not existing and code not in [c['code'] for c in codes]:
                        # 创建邀请码
                        invitation_code = self.repository.create_code(
                            code=code,
                            code_type=code_type,
                            created_by=created_by
                        )
                        codes.append({
                            'id': invitation_code.id,
                            'code': invitation_code.code,
                            'code_display': invitation_code.format_display(),
                            'created_at': invitation_code.created_at.isoformat()
                        })
                        success = True
                        break
                
                if not success:
                    failed_count += 1
            
            if failed_count > 0:
                return service_error_response("PARTIAL_GENERATION_FAILED", 
                    f"成功生成 {len(codes)} 个邀请码，{failed_count} 个失败")
            
            self.db.commit()
            
            return service_success_response({
                'codes': codes,
                'count': len(codes)
            })
            
        except Exception as e:
            self.db.rollback()
            return service_error_response("GENERATION_ERROR", f"批量生成邀请码时发生错误: {str(e)}")
    
    def validate_code(self, code: str, code_type: str = 'INVITATION') -> Dict:
        """
        验证邀请码有效性
        
        Args:
            code: 邀请码（会自动标准化）
            code_type: 码类型
            
        Returns:
            验证结果
        """
        try:
            normalized_code = InvitationCode.normalize_code(code)
            if not normalized_code or len(normalized_code) != 18:
                return service_error_response("INVALID_FORMAT", "邀请码格式不正确（应为18个字符）")
            
            invitation_code = self.repository.get_by_code(normalized_code)
            
            if not invitation_code:
                return service_error_response("CODE_NOT_FOUND", "邀请码不存在")
            
            if invitation_code.code_type != code_type:
                return service_error_response("CODE_TYPE_MISMATCH", "邀请码类型不匹配")
            
            if invitation_code.is_used:
                return service_error_response("CODE_ALREADY_USED", "邀请码已被使用")
            
            return service_success_response({
                'id': invitation_code.id,
                'code': invitation_code.code,
                'is_valid': True
            })
            
        except Exception as e:
            return service_error_response("VALIDATION_ERROR", f"验证邀请码时发生错误: {str(e)}")
    
    def use_code(self, code_id: int, user_id: int) -> Dict:
        """
        使用邀请码（标记为已使用）
        
        Args:
            code_id: 邀请码ID
            user_id: 使用者ID
            
        Returns:
            使用结果
        """
        try:
            success = self.repository.mark_as_used(code_id, user_id)
            if not success:
                return service_error_response("USE_FAILED", "标记邀请码失败（可能已被使用）")
            
            self.db.commit()
            
            return service_success_response({
                'code_id': code_id,
                'user_id': user_id
            })
            
        except Exception as e:
            self.db.rollback()
            return service_error_response("USE_ERROR", f"使用邀请码时发生错误: {str(e)}")
    
    def get_code_list(self, code_type: str = 'INVITATION', status: Optional[str] = None,
                     page: int = 1, per_page: int = 20) -> Dict:
        """
        获取邀请码列表（分页）
        
        Args:
            code_type: 码类型
            status: 状态筛选（all/used/unused）
            page: 页码
            per_page: 每页数量
            
        Returns:
            邀请码列表和分页信息
        """
        try:
            result = self.repository.get_all_codes(
                code_type=code_type,
                status=status,
                page=page,
                per_page=per_page
            )
            
            codes_data = [code.to_dict(include_user=True) for code in result['codes']]
            
            return service_success_response({
                'codes': codes_data,
                'pagination': result['pagination']
            })
            
        except Exception as e:
            return service_error_response("GET_LIST_ERROR", f"获取邀请码列表失败: {str(e)}")
    
    def get_code_detail(self, code_id: int) -> Dict:
        """
        获取邀请码详情
        
        Args:
            code_id: 邀请码ID
            
        Returns:
            邀请码详情
        """
        try:
            code = self.repository.get_by_id(code_id)
            if not code:
                return service_error_response("CODE_NOT_FOUND", "邀请码不存在")
            
            return service_success_response(code.to_dict(include_user=True))
            
        except Exception as e:
            return service_error_response("GET_DETAIL_ERROR", f"获取邀请码详情失败: {str(e)}")
    
    def get_statistics(self, code_type: str = 'INVITATION') -> Dict:
        """
        获取邀请码统计信息
        
        Args:
            code_type: 码类型
            
        Returns:
            统计信息
        """
        try:
            stats = self.repository.get_statistics(code_type=code_type)
            return service_success_response(stats)
            
        except Exception as e:
            return service_error_response("GET_STATS_ERROR", f"获取统计信息失败: {str(e)}")
    
    def export_unused_codes(self, code_type: str = 'INVITATION') -> Dict:
        """
        导出未使用的邀请码列表（用于CSV导出）
        
        Args:
            code_type: 码类型
            
        Returns:
            未使用的邀请码列表
        """
        try:
            codes = self.repository.get_unused_codes(code_type=code_type)
            
            codes_data = []
            for code in codes:
                codes_data.append({
                    'code': code.code,
                    'code_display': code.format_display(),
                    'created_at': code.created_at.isoformat() if code.created_at else None,
                    'creator': code.creator.username if code.creator else None
                })
            
            return service_success_response({
                'codes': codes_data,
                'count': len(codes_data)
            })
            
        except Exception as e:
            return service_error_response("EXPORT_ERROR", f"导出邀请码失败: {str(e)}")

