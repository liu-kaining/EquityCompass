"""
基础数据访问接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session


class BaseRepository(ABC):
    """数据访问基础接口"""
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Any:
        """创建数据"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[Any]:
        """根据ID获取数据"""
        pass
    
    @abstractmethod
    def get_all(self, **filters) -> List[Any]:
        """获取所有数据（支持过滤）"""
        pass
    
    @abstractmethod
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[Any]:
        """更新数据"""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """删除数据"""
        pass
    
    @abstractmethod
    def count(self, **filters) -> int:
        """统计数据量"""
        pass


class SQLAlchemyRepository(BaseRepository):
    """SQLAlchemy实现的基础Repository"""
    
    def __init__(self, model_class, session: Session):
        self.model_class = model_class
        self.session = session
    
    def create(self, data: Dict[str, Any]) -> Any:
        """创建数据"""
        instance = self.model_class(**data)
        self.session.add(instance)
        self.session.commit()
        return instance
    
    def get_by_id(self, id: Any) -> Optional[Any]:
        """根据ID获取数据"""
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).first()
    
    def get_all(self, **filters) -> List[Any]:
        """获取所有数据（支持过滤）"""
        query = self.session.query(self.model_class)
        
        # 应用过滤条件
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        
        return query.all()
    
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[Any]:
        """更新数据"""
        instance = self.get_by_id(id)
        if instance:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.session.commit()
        return instance
    
    def delete(self, id: Any) -> bool:
        """删除数据"""
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False
    
    def count(self, **filters) -> int:
        """统计数据量"""
        query = self.session.query(self.model_class)
        
        # 应用过滤条件
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        
        return query.count()


class JSONRepository(BaseRepository):
    """JSON文件实现的Repository（用于报告存储）"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def create(self, data: Dict[str, Any]) -> Any:
        """创建数据（写入JSON文件）"""
        import json
        import os
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        # 写入JSON文件
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return data
    
    def get_by_id(self, id: Any) -> Optional[Any]:
        """根据ID获取数据（读取JSON文件）"""
        import json
        import os
        
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('id') == id:
                        return data
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return None
    
    def get_all(self, **filters) -> List[Any]:
        """获取所有数据（暂不实现）"""
        # JSON存储主要用于单个报告文件
        raise NotImplementedError("JSON Repository暂不支持get_all操作")
    
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[Any]:
        """更新数据"""
        current_data = self.get_by_id(id)
        if current_data:
            current_data.update(data)
            return self.create(current_data)
        return None
    
    def delete(self, id: Any) -> bool:
        """删除数据（删除文件）"""
        import os
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            return True
        return False
    
    def count(self, **filters) -> int:
        """统计数据量"""
        return 1 if self.get_by_id(filters.get('id')) else 0
