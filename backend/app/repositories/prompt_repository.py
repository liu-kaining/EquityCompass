"""
提示词数据访问层
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.prompt import Prompt


class PromptRepository:
    """提示词数据访问类"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_all(self) -> List[Prompt]:
        """获取所有提示词"""
        return self.session.query(Prompt).order_by(Prompt.prompt_type, Prompt.name, Prompt.version.desc()).all()
    
    def get_by_id(self, prompt_id: int) -> Optional[Prompt]:
        """根据ID获取提示词"""
        return self.session.query(Prompt).filter_by(id=prompt_id).first()
    
    def get_by_name(self, name: str) -> List[Prompt]:
        """根据名称获取所有版本的提示词"""
        return self.session.query(Prompt).filter_by(name=name).order_by(Prompt.version.desc()).all()
    
    def get_by_type(self, prompt_type: str) -> List[Prompt]:
        """根据类型获取提示词"""
        return self.session.query(Prompt).filter_by(prompt_type=prompt_type).order_by(Prompt.name, Prompt.version.desc()).all()
    
    def get_active_by_type(self, prompt_type: str) -> List[Prompt]:
        """获取指定类型的激活提示词"""
        return self.session.query(Prompt).filter_by(prompt_type=prompt_type, is_active=True).order_by(Prompt.is_default.desc(), Prompt.version.desc()).all()
    
    def get_default_by_type(self, prompt_type: str) -> Optional[Prompt]:
        """获取指定类型的默认提示词"""
        return self.session.query(Prompt).filter_by(prompt_type=prompt_type, is_default=True, is_active=True).first()
    
    def get_latest_version(self, name: str) -> Optional[Prompt]:
        """获取指定名称的最新版本"""
        return self.session.query(Prompt).filter_by(name=name).order_by(Prompt.version.desc()).first()
    
    def create_prompt(self, prompt_data: Dict[str, Any]) -> Prompt:
        """创建新的提示词"""
        prompt = Prompt(
            name=prompt_data['name'],
            description=prompt_data.get('description'),
            prompt_type=prompt_data['prompt_type'],
            content=prompt_data['content'],
            version=prompt_data.get('version', 1),
            is_active=prompt_data.get('is_active', True),
            is_default=prompt_data.get('is_default', False),
            created_by=prompt_data.get('created_by')
        )
        
        self.session.add(prompt)
        self.session.commit()
        return prompt
    
    def update_prompt(self, prompt_id: int, prompt_data: Dict[str, Any]) -> Optional[Prompt]:
        """更新提示词"""
        prompt = self.get_by_id(prompt_id)
        if not prompt:
            return None
        
        # 更新字段
        for key, value in prompt_data.items():
            if hasattr(prompt, key):
                setattr(prompt, key, value)
        
        self.session.commit()
        return prompt
    
    def delete_prompt(self, prompt_id: int) -> bool:
        """删除提示词"""
        prompt = self.get_by_id(prompt_id)
        if not prompt:
            return False
        
        self.session.delete(prompt)
        self.session.commit()
        return True
    
    def toggle_active(self, prompt_id: int) -> Optional[Prompt]:
        """切换提示词的激活状态"""
        prompt = self.get_by_id(prompt_id)
        if not prompt:
            return None
        
        prompt.is_active = not prompt.is_active
        self.session.commit()
        return prompt
    
    def set_default_version(self, prompt_id: int) -> bool:
        """设置默认版本"""
        prompt = self.get_by_id(prompt_id)
        if not prompt:
            return False
        
        # 先清除同类型的所有默认标记
        self.session.query(Prompt).filter_by(prompt_type=prompt.prompt_type).update({'is_default': False})
        
        # 设置新的默认版本
        prompt.is_default = True
        self.session.commit()
        return True
    
    def create_new_version(self, name: str, prompt_type: str, content: str, description: str = None, created_by: int = None) -> Prompt:
        """创建新版本"""
        # 获取当前最新版本号
        latest = self.get_latest_version(name)
        new_version = (latest.version + 1) if latest else 1
        
        # 创建新版本
        new_prompt = Prompt(
            name=name,
            description=description,
            prompt_type=prompt_type,
            content=content,
            version=new_version,
            created_by=created_by
        )
        
        self.session.add(new_prompt)
        self.session.commit()
        return new_prompt
    
    def increment_usage(self, prompt_id: int) -> bool:
        """增加使用次数"""
        prompt = self.get_by_id(prompt_id)
        if not prompt:
            return False
        
        prompt.increment_usage()
        return True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        total_prompts = self.session.query(Prompt).count()
        active_prompts = self.session.query(Prompt).filter_by(is_active=True).count()
        
        # 计算总体使用统计
        from sqlalchemy import func
        total_usage = self.session.query(func.sum(Prompt.usage_count)).scalar() or 0
        
        # 获取最常用的提示词
        most_used = self.session.query(Prompt).order_by(Prompt.usage_count.desc()).first()
        
        return {
            'total_prompts': total_prompts,
            'active_prompts': active_prompts,
            'total_usage': total_usage,
            'most_used_prompt': most_used.name if most_used else None,
            'most_used_count': most_used.usage_count if most_used else 0
        }
    
    def get_prompt_types(self) -> List[str]:
        """获取所有提示词类型"""
        types = self.session.query(Prompt.prompt_type).distinct().all()
        return [t[0] for t in types]
    
    def get_prompt_names(self) -> List[str]:
        """获取所有提示词名称"""
        names = self.session.query(Prompt.name).distinct().all()
        return [n[0] for n in names]
    
    def search_prompts(self, query: str) -> List[Prompt]:
        """搜索提示词"""
        return self.session.query(Prompt).filter(
            (Prompt.name.contains(query)) | 
            (Prompt.description.contains(query)) |
            (Prompt.content.contains(query))
        ).order_by(Prompt.prompt_type, Prompt.name, Prompt.version.desc()).all()
