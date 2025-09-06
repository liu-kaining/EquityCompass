"""
提示词业务逻辑层
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.prompt_repository import PromptRepository
from app.models.prompt import Prompt

logger = logging.getLogger(__name__)


class PromptService:
    """提示词服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repo = PromptRepository(session)
    
    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """获取所有提示词"""
        try:
            prompts = self.repo.get_all()
            return [prompt.to_dict() for prompt in prompts]
        except Exception as e:
            logger.error(f"获取提示词失败: {str(e)}")
            return []
    
    def get_prompt_by_id(self, prompt_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取提示词"""
        try:
            prompt = self.repo.get_by_id(prompt_id)
            if prompt:
                return prompt.to_dict()
            return None
        except Exception as e:
            logger.error(f"获取提示词失败: {str(e)}")
            return None
    
    def get_prompts_by_type(self, prompt_type: str) -> List[Dict[str, Any]]:
        """根据类型获取提示词"""
        try:
            prompts = self.repo.get_active_by_type(prompt_type)
            return [prompt.to_dict() for prompt in prompts]
        except Exception as e:
            logger.error(f"获取提示词失败: {str(e)}")
            return []
    
    def get_default_prompt(self, prompt_type: str) -> Optional[Dict[str, Any]]:
        """获取默认提示词"""
        try:
            prompt = self.repo.get_default_by_type(prompt_type)
            if prompt:
                return prompt.to_dict()
            return None
        except Exception as e:
            logger.error(f"获取默认提示词失败: {str(e)}")
            return None
    
    def get_prompt_versions(self, name: str) -> List[Dict[str, Any]]:
        """获取提示词的所有版本"""
        try:
            prompts = self.repo.get_by_name(name)
            return [prompt.to_dict() for prompt in prompts]
        except Exception as e:
            logger.error(f"获取提示词版本失败: {str(e)}")
            return []
    
    def create_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的提示词"""
        try:
            # 验证必填字段
            required_fields = ['name', 'prompt_type', 'content']
            for field in required_fields:
                if not prompt_data.get(field):
                    return {'success': False, 'error': f'缺少必填字段: {field}'}
            
            # 检查是否已存在同名提示词
            existing_prompts = self.repo.get_by_name(prompt_data['name'])
            if existing_prompts:
                # 如果已存在，创建新版本
                new_prompt = self.repo.create_new_version(
                    name=prompt_data['name'],
                    prompt_type=prompt_data['prompt_type'],
                    content=prompt_data['content'],
                    description=prompt_data.get('description'),
                    created_by=prompt_data.get('created_by')
                )
                logger.info(f"创建提示词新版本: {new_prompt.name} v{new_prompt.version}")
            else:
                # 创建新提示词
                new_prompt = self.repo.create_prompt(prompt_data)
                logger.info(f"创建新提示词: {new_prompt.name}")
            
            return {
                'success': True,
                'data': new_prompt.to_dict(),
                'message': '提示词创建成功'
            }
            
        except Exception as e:
            logger.error(f"创建提示词失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_prompt(self, prompt_id: int, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新提示词"""
        try:
            # 检查提示词是否存在
            existing_prompt = self.repo.get_by_id(prompt_id)
            if not existing_prompt:
                return {'success': False, 'error': '提示词不存在'}
            
            # 更新提示词
            updated_prompt = self.repo.update_prompt(prompt_id, prompt_data)
            if updated_prompt:
                logger.info(f"更新提示词成功: {updated_prompt.name}")
                return {
                    'success': True,
                    'data': updated_prompt.to_dict(),
                    'message': '提示词更新成功'
                }
            else:
                return {'success': False, 'error': '更新失败'}
                
        except Exception as e:
            logger.error(f"更新提示词失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_prompt(self, prompt_id: int) -> Dict[str, Any]:
        """删除提示词"""
        try:
            prompt = self.repo.get_by_id(prompt_id)
            if not prompt:
                return {'success': False, 'error': '提示词不存在'}
            
            # 检查是否为默认提示词
            if prompt.is_default:
                return {'success': False, 'error': '不能删除默认提示词，请先设置其他提示词为默认'}
            
            prompt_name = prompt.name
            success = self.repo.delete_prompt(prompt_id)
            
            if success:
                logger.info(f"删除提示词成功: {prompt_name}")
                return {'success': True, 'message': '提示词删除成功'}
            else:
                return {'success': False, 'error': '删除失败'}
                
        except Exception as e:
            logger.error(f"删除提示词失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def toggle_active(self, prompt_id: int) -> Dict[str, Any]:
        """切换提示词激活状态"""
        try:
            prompt = self.repo.get_by_id(prompt_id)
            if not prompt:
                return {'success': False, 'error': '提示词不存在'}
            
            # 如果是默认提示词且要设为非激活，需要先设置其他提示词为默认
            if prompt.is_default and prompt.is_active:
                active_prompts = self.repo.get_active_by_type(prompt.prompt_type)
                other_active_prompts = [p for p in active_prompts if p.id != prompt_id]
                if not other_active_prompts:
                    return {'success': False, 'error': '不能停用最后一个激活的提示词'}
            
            updated_prompt = self.repo.toggle_active(prompt_id)
            if updated_prompt:
                status = '激活' if updated_prompt.is_active else '停用'
                logger.info(f"{status}提示词: {updated_prompt.name}")
                return {
                    'success': True,
                    'data': updated_prompt.to_dict(),
                    'message': f'提示词已{status}'
                }
            else:
                return {'success': False, 'error': '操作失败'}
                
        except Exception as e:
            logger.error(f"切换提示词状态失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def set_default_version(self, prompt_id: int) -> Dict[str, Any]:
        """设置默认版本"""
        try:
            prompt = self.repo.get_by_id(prompt_id)
            if not prompt:
                return {'success': False, 'error': '提示词不存在'}
            
            if not prompt.is_active:
                return {'success': False, 'error': '不能设置非激活提示词为默认'}
            
            success = self.repo.set_default_version(prompt_id)
            if success:
                logger.info(f"设置默认提示词: {prompt.name}")
                return {'success': True, 'message': f'已设置 {prompt.name} v{prompt.version} 为默认提示词'}
            else:
                return {'success': False, 'error': '设置失败'}
                
        except Exception as e:
            logger.error(f"设置默认提示词失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_new_version(self, name: str, prompt_type: str, content: str, description: str = None, created_by: int = None) -> Dict[str, Any]:
        """创建新版本"""
        try:
            new_prompt = self.repo.create_new_version(name, prompt_type, content, description, created_by)
            logger.info(f"创建提示词新版本: {new_prompt.name} v{new_prompt.version}")
            return {
                'success': True,
                'data': new_prompt.to_dict(),
                'message': f'已创建 {new_prompt.name} v{new_prompt.version}'
            }
        except Exception as e:
            logger.error(f"创建新版本失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def increment_usage(self, prompt_id: int) -> bool:
        """增加使用次数"""
        try:
            return self.repo.increment_usage(prompt_id)
        except Exception as e:
            logger.error(f"增加使用次数失败: {str(e)}")
            return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        try:
            return self.repo.get_usage_stats()
        except Exception as e:
            logger.error(f"获取使用统计失败: {str(e)}")
            return {
                'total_prompts': 0,
                'active_prompts': 0,
                'total_usage': 0,
                'most_used_prompt': None,
                'most_used_count': 0
            }
    
    def get_prompt_types(self) -> List[str]:
        """获取所有提示词类型"""
        try:
            return self.repo.get_prompt_types()
        except Exception as e:
            logger.error(f"获取提示词类型失败: {str(e)}")
            return []
    
    def search_prompts(self, query: str) -> List[Dict[str, Any]]:
        """搜索提示词"""
        try:
            prompts = self.repo.search_prompts(query)
            return [prompt.to_dict() for prompt in prompts]
        except Exception as e:
            logger.error(f"搜索提示词失败: {str(e)}")
            return []
    
    def import_default_prompts(self) -> Dict[str, Any]:
        """导入默认提示词"""
        try:
            from app.config.prompts import FUNDAMENTAL_ANALYSIS_PROMPT, TECHNICAL_ANALYSIS_PROMPT
            
            imported_count = 0
            
            # 检查基础分析提示词是否存在
            existing_fundamental = self.repo.get_by_name("基础分析提示词")
            if not existing_fundamental:
                self.repo.create_prompt({
                    'name': '基础分析提示词',
                    'description': '用于股票基础分析的默认提示词',
                    'prompt_type': 'fundamental',
                    'content': FUNDAMENTAL_ANALYSIS_PROMPT,
                    'is_default': True,
                    'created_by': 1  # 系统用户
                })
                imported_count += 1
                logger.info("导入基础分析提示词")
            
            # 检查技术分析提示词是否存在
            existing_technical = self.repo.get_by_name("技术分析提示词")
            if not existing_technical:
                self.repo.create_prompt({
                    'name': '技术分析提示词',
                    'description': '用于股票技术分析的默认提示词',
                    'prompt_type': 'technical',
                    'content': TECHNICAL_ANALYSIS_PROMPT,
                    'is_default': True,
                    'created_by': 1  # 系统用户
                })
                imported_count += 1
                logger.info("导入技术分析提示词")
            
            return {
                'success': True,
                'message': f'成功导入 {imported_count} 个默认提示词',
                'imported_count': imported_count
            }
            
        except Exception as e:
            logger.error(f"导入默认提示词失败: {str(e)}")
            return {'success': False, 'error': str(e)}
