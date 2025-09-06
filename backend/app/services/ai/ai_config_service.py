"""
AI配置业务逻辑层
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.ai_config_repository import AIConfigRepository
from app.models.ai_config import AIConfig

logger = logging.getLogger(__name__)


class AIConfigService:
    """AI配置服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repo = AIConfigRepository(session)
    
    def get_all_configs(self, include_sensitive: bool = False) -> List[Dict[str, Any]]:
        """获取所有AI配置"""
        try:
            configs = self.repo.get_all()
            return [config.to_dict(include_sensitive=include_sensitive) for config in configs]
        except Exception as e:
            logger.error(f"获取AI配置失败: {str(e)}")
            return []
    
    def get_config_by_id(self, config_id: int, include_sensitive: bool = False) -> Optional[Dict[str, Any]]:
        """根据ID获取配置"""
        try:
            config = self.repo.get_by_id(config_id)
            if config:
                return config.to_dict(include_sensitive=include_sensitive)
            return None
        except Exception as e:
            logger.error(f"获取AI配置失败: {str(e)}")
            return None
    
    def get_active_configs(self) -> List[Dict[str, Any]]:
        """获取激活的配置"""
        try:
            configs = self.repo.get_active_configs()
            return [config.to_dict() for config in configs]
        except Exception as e:
            logger.error(f"获取激活配置失败: {str(e)}")
            return []
    
    def get_default_config(self) -> Optional[Dict[str, Any]]:
        """获取默认配置"""
        try:
            config = self.repo.get_default_config()
            if config:
                return config.to_dict()
            return None
        except Exception as e:
            logger.error(f"获取默认配置失败: {str(e)}")
            return None
    
    def create_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的AI配置"""
        try:
            # 验证必填字段
            required_fields = ['provider_name', 'display_name', 'api_key', 'model_name']
            for field in required_fields:
                if not config_data.get(field):
                    return {'success': False, 'error': f'缺少必填字段: {field}'}
            
            # 检查提供商名称是否已存在
            existing_config = self.repo.get_by_provider(config_data['provider_name'])
            if existing_config:
                return {'success': False, 'error': f'提供商 {config_data["provider_name"]} 已存在'}
            
            # 如果是第一个配置，自动设为默认
            if not self.repo.get_all():
                config_data['is_default'] = True
            
            # 创建配置
            config = self.repo.create_config(config_data)
            
            logger.info(f"创建AI配置成功: {config.provider_name}")
            return {
                'success': True,
                'data': config.to_dict(),
                'message': '配置创建成功'
            }
            
        except Exception as e:
            logger.error(f"创建AI配置失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_config(self, config_id: int, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新AI配置"""
        try:
            # 检查配置是否存在
            existing_config = self.repo.get_by_id(config_id)
            if not existing_config:
                return {'success': False, 'error': '配置不存在'}
            
            # 如果更新提供商名称，检查是否与其他配置冲突
            if 'provider_name' in config_data and config_data['provider_name'] != existing_config.provider_name:
                conflict_config = self.repo.get_by_provider(config_data['provider_name'])
                if conflict_config and conflict_config.id != config_id:
                    return {'success': False, 'error': f'提供商 {config_data["provider_name"]} 已存在'}
            
            # 更新配置
            updated_config = self.repo.update_config(config_id, config_data)
            if updated_config:
                logger.info(f"更新AI配置成功: {updated_config.provider_name}")
                return {
                    'success': True,
                    'data': updated_config.to_dict(),
                    'message': '配置更新成功'
                }
            else:
                return {'success': False, 'error': '更新失败'}
                
        except Exception as e:
            logger.error(f"更新AI配置失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_config(self, config_id: int) -> Dict[str, Any]:
        """删除AI配置"""
        try:
            config = self.repo.get_by_id(config_id)
            if not config:
                return {'success': False, 'error': '配置不存在'}
            
            # 检查是否为默认配置
            if config.is_default:
                return {'success': False, 'error': '不能删除默认配置，请先设置其他配置为默认'}
            
            provider_name = config.provider_name
            success = self.repo.delete_config(config_id)
            
            if success:
                logger.info(f"删除AI配置成功: {provider_name}")
                return {'success': True, 'message': '配置删除成功'}
            else:
                return {'success': False, 'error': '删除失败'}
                
        except Exception as e:
            logger.error(f"删除AI配置失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def toggle_active(self, config_id: int) -> Dict[str, Any]:
        """切换配置激活状态"""
        try:
            config = self.repo.get_by_id(config_id)
            if not config:
                return {'success': False, 'error': '配置不存在'}
            
            # 如果是默认配置且要设为非激活，需要先设置其他配置为默认
            if config.is_default and config.is_active:
                active_configs = self.repo.get_active_configs()
                other_active_configs = [c for c in active_configs if c.id != config_id]
                if not other_active_configs:
                    return {'success': False, 'error': '不能停用最后一个激活的配置'}
            
            updated_config = self.repo.toggle_active(config_id)
            if updated_config:
                status = '激活' if updated_config.is_active else '停用'
                logger.info(f"{status}AI配置: {updated_config.provider_name}")
                return {
                    'success': True,
                    'data': updated_config.to_dict(),
                    'message': f'配置已{status}'
                }
            else:
                return {'success': False, 'error': '操作失败'}
                
        except Exception as e:
            logger.error(f"切换配置状态失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def set_default_config(self, config_id: int) -> Dict[str, Any]:
        """设置默认配置"""
        try:
            config = self.repo.get_by_id(config_id)
            if not config:
                return {'success': False, 'error': '配置不存在'}
            
            if not config.is_active:
                return {'success': False, 'error': '不能设置非激活配置为默认'}
            
            success = self.repo.set_default_config(config_id)
            if success:
                logger.info(f"设置默认AI配置: {config.provider_name}")
                return {'success': True, 'message': f'已设置 {config.display_name} 为默认配置'}
            else:
                return {'success': False, 'error': '设置失败'}
                
        except Exception as e:
            logger.error(f"设置默认配置失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_config(self, config_id: int) -> Dict[str, Any]:
        """测试配置连接"""
        try:
            config = self.repo.get_by_id(config_id)
            if not config:
                return {'success': False, 'error': '配置不存在'}
            
            result = self.repo.test_config(config_id)
            logger.info(f"测试AI配置: {config.provider_name}, 结果: {result['success']}")
            return result
            
        except Exception as e:
            logger.error(f"测试配置失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        try:
            return self.repo.get_usage_stats()
        except Exception as e:
            logger.error(f"获取使用统计失败: {str(e)}")
            return {
                'total_configs': 0,
                'active_configs': 0,
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'success_rate': 0.0
            }
    
    def get_provider_templates(self) -> Dict[str, Dict[str, Any]]:
        """获取提供商配置模板"""
        return {
            'qwen': {
                'provider_name': 'qwen',
                'display_name': '通义千问',
                'api_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                'model_name': 'qwen-deep-research',
                'advanced_config': {
                    'max_tokens': 15000,
                    'temperature': 0.7,
                    'enable_deep_thinking': True,
                    'enable_web_search': True,
                    'thinking_steps': 3
                }
            },
            'deepseek': {
                'provider_name': 'deepseek',
                'display_name': 'DeepSeek',
                'api_url': 'https://api.deepseek.com/v1/chat/completions',
                'model_name': 'deepseek-reasoner',
                'advanced_config': {
                    'max_tokens': 15000,
                    'temperature': 0.7,
                    'enable_deep_thinking': True,
                    'thinking_steps': 3
                }
            },
            'gemini': {
                'provider_name': 'gemini',
                'display_name': 'Google Gemini',
                'api_url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
                'model_name': 'gemini-2.0-flash',
                'advanced_config': {
                    'max_tokens': 15000,
                    'temperature': 0.7
                }
            },
            'openai': {
                'provider_name': 'openai',
                'display_name': 'OpenAI',
                'api_url': 'https://api.openai.com/v1/chat/completions',
                'model_name': 'gpt-4',
                'advanced_config': {
                    'max_tokens': 15000,
                    'temperature': 0.7
                }
            }
        }
    
    def import_from_env(self) -> Dict[str, Any]:
        """从环境变量导入配置"""
        try:
            import os
            imported_count = 0
            
            # 检查环境变量中的配置
            env_configs = {
                'qwen': {
                    'api_key': os.getenv('QWEN_API_KEY'),
                    'model': os.getenv('QWEN_MODEL', 'qwen-deep-research')
                },
                'deepseek': {
                    'api_key': os.getenv('DEEPSEEK_API_KEY'),
                    'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner')
                },
                'gemini': {
                    'api_key': os.getenv('GEMINI_API_KEY'),
                    'model': os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
                },
                'openai': {
                    'api_key': os.getenv('OPENAI_API_KEY'),
                    'model': os.getenv('OPENAI_MODEL', 'gpt-4')
                }
            }
            
            templates = self.get_provider_templates()
            
            for provider, env_data in env_configs.items():
                if env_data['api_key']:
                    # 检查是否已存在
                    existing = self.repo.get_by_provider(provider)
                    if not existing:
                        # 创建配置
                        config_data = templates[provider].copy()
                        config_data['api_key'] = env_data['api_key']
                        config_data['model_name'] = env_data['model']
                        
                        self.repo.create_config(config_data)
                        imported_count += 1
                        logger.info(f"从环境变量导入配置: {provider}")
            
            return {
                'success': True,
                'message': f'成功导入 {imported_count} 个配置',
                'imported_count': imported_count
            }
            
        except Exception as e:
            logger.error(f"从环境变量导入配置失败: {str(e)}")
            return {'success': False, 'error': str(e)}
