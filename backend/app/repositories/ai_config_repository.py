"""
AI配置数据访问层
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.ai_config import AIConfig


class AIConfigRepository:
    """AI配置数据访问类"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_all(self) -> List[AIConfig]:
        """获取所有AI配置"""
        return self.session.query(AIConfig).order_by(AIConfig.created_at.desc()).all()
    
    def get_by_id(self, config_id: int) -> Optional[AIConfig]:
        """根据ID获取配置"""
        return self.session.query(AIConfig).filter_by(id=config_id).first()
    
    def get_by_provider(self, provider_name: str) -> Optional[AIConfig]:
        """根据提供商名称获取配置"""
        return self.session.query(AIConfig).filter_by(provider_name=provider_name).first()
    
    def get_active_configs(self) -> List[AIConfig]:
        """获取所有激活的配置"""
        return self.session.query(AIConfig).filter_by(is_active=True).order_by(AIConfig.is_default.desc(), AIConfig.created_at.desc()).all()
    
    def get_default_config(self) -> Optional[AIConfig]:
        """获取默认配置"""
        return self.session.query(AIConfig).filter_by(is_default=True, is_active=True).first()
    
    def create_config(self, config_data: Dict[str, Any]) -> AIConfig:
        """创建新的AI配置"""
        config = AIConfig(
            provider_name=config_data['provider_name'],
            display_name=config_data['display_name'],
            api_key=config_data['api_key'],
            model_name=config_data['model_name'],
            api_url=config_data.get('api_url'),
            advanced_config=config_data.get('advanced_config', {}),
            is_active=config_data.get('is_active', True),
            is_default=config_data.get('is_default', False),
            created_by=config_data.get('created_by')
        )
        
        self.session.add(config)
        self.session.commit()
        return config
    
    def update_config(self, config_id: int, config_data: Dict[str, Any]) -> Optional[AIConfig]:
        """更新AI配置"""
        config = self.get_by_id(config_id)
        if not config:
            return None
        
        # 更新字段
        for key, value in config_data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.session.commit()
        return config
    
    def delete_config(self, config_id: int) -> bool:
        """删除AI配置"""
        config = self.get_by_id(config_id)
        if not config:
            return False
        
        self.session.delete(config)
        self.session.commit()
        return True
    
    def toggle_active(self, config_id: int) -> Optional[AIConfig]:
        """切换配置的激活状态"""
        config = self.get_by_id(config_id)
        if not config:
            return None
        
        config.is_active = not config.is_active
        self.session.commit()
        return config
    
    def set_default_config(self, config_id: int) -> bool:
        """设置默认配置"""
        # 先清除所有默认标记
        self.session.query(AIConfig).update({'is_default': False})
        
        # 设置新的默认配置
        config = self.get_by_id(config_id)
        if config:
            config.is_default = True
            self.session.commit()
            return True
        return False
    
    def update_usage_stats(self, config_id: int, success: bool = True) -> bool:
        """更新使用统计"""
        config = self.get_by_id(config_id)
        if not config:
            return False
        
        config.update_usage_stats(success)
        return True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        total_configs = self.session.query(AIConfig).count()
        active_configs = self.session.query(AIConfig).filter_by(is_active=True).count()
        
        # 计算总体使用统计
        from sqlalchemy import func
        total_requests = self.session.query(func.sum(AIConfig.total_requests)).scalar() or 0
        successful_requests = self.session.query(func.sum(AIConfig.successful_requests)).scalar() or 0
        failed_requests = self.session.query(func.sum(AIConfig.failed_requests)).scalar() or 0
        
        success_rate = 0.0
        if total_requests > 0:
            success_rate = round((successful_requests / total_requests) * 100, 2)
        
        return {
            'total_configs': total_configs,
            'active_configs': active_configs,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': success_rate
        }
    
    def test_config(self, config_id: int) -> Dict[str, Any]:
        """测试配置连接"""
        config = self.get_by_id(config_id)
        if not config:
            return {'success': False, 'error': '配置不存在'}
        
        try:
            from app.services.ai.llm_provider import LLMProviderFactory
            
            # 创建Provider并测试连接
            provider = LLMProviderFactory.create_provider(
                config.provider_name, 
                config.get_config_dict()
            )
            
            is_connected = provider.test_connection()
            
            # 更新使用统计
            self.update_usage_stats(config_id, is_connected)
            
            return {
                'success': is_connected,
                'message': '连接成功' if is_connected else '连接失败，请检查API密钥和网络连接',
                'provider': config.provider_name,
                'model': config.model_name
            }
            
        except Exception as e:
            self.update_usage_stats(config_id, False)
            return {
                'success': False,
                'message': f'连接测试失败: {str(e)}',
                'provider': config.provider_name,
                'model': config.model_name
            }
