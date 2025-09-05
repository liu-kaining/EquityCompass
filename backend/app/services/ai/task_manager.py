"""
任务管理器 - 管理异步任务的暂停、恢复和取消
"""
import threading
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskManager:
    """任务管理器单例"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TaskManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._tasks: Dict[str, Dict] = {}  # task_id -> task_info
            self._task_lock = threading.RLock()
            self._initialized = True
    
    def register_task(self, task_id: str, thread: threading.Thread, task_type: str = 'analysis') -> None:
        """注册任务"""
        with self._task_lock:
            self._tasks[task_id] = {
                'thread': thread,
                'pause_event': threading.Event(),  # 用于暂停/恢复
                'stop_event': threading.Event(),   # 用于停止任务
                'task_type': task_type,
                'created_at': datetime.utcnow(),
                'status': 'running'
            }
            logger.info(f"任务 {task_id} 已注册到任务管理器")
    
    def unregister_task(self, task_id: str) -> None:
        """注销任务"""
        with self._task_lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                logger.info(f"任务 {task_id} 已从任务管理器注销")
    
    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        with self._task_lock:
            if task_id not in self._tasks:
                logger.warning(f"任务 {task_id} 不存在于任务管理器中")
                return False
            
            task_info = self._tasks[task_id]
            if task_info['status'] != 'running':
                logger.warning(f"任务 {task_id} 状态为 {task_info['status']}，无法暂停")
                return False
            
            # 设置暂停事件
            task_info['pause_event'].set()
            task_info['status'] = 'paused'
            task_info['paused_at'] = datetime.utcnow()
            
            logger.info(f"任务 {task_id} 已暂停")
            return True
    
    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        with self._task_lock:
            if task_id not in self._tasks:
                logger.warning(f"任务 {task_id} 不存在于任务管理器中")
                return False
            
            task_info = self._tasks[task_id]
            if task_info['status'] != 'paused':
                logger.warning(f"任务 {task_id} 状态为 {task_info['status']}，无法恢复")
                return False
            
            # 清除暂停事件
            task_info['pause_event'].clear()
            task_info['status'] = 'running'
            task_info['resumed_at'] = datetime.utcnow()
            
            logger.info(f"任务 {task_id} 已恢复")
            return True
    
    def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        with self._task_lock:
            if task_id not in self._tasks:
                logger.warning(f"任务 {task_id} 不存在于任务管理器中")
                return False
            
            task_info = self._tasks[task_id]
            
            # 设置停止事件
            task_info['stop_event'].set()
            task_info['status'] = 'stopped'
            task_info['stopped_at'] = datetime.utcnow()
            
            logger.info(f"任务 {task_id} 已停止")
            return True
    
    def is_task_paused(self, task_id: str) -> bool:
        """检查任务是否被暂停"""
        with self._task_lock:
            if task_id not in self._tasks:
                return False
            return self._tasks[task_id]['pause_event'].is_set()
    
    def is_task_stopped(self, task_id: str) -> bool:
        """检查任务是否被停止"""
        with self._task_lock:
            if task_id not in self._tasks:
                return False
            return self._tasks[task_id]['stop_event'].is_set()
    
    def wait_if_paused(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """如果任务被暂停，则等待恢复。返回True表示任务继续，False表示任务被停止"""
        with self._task_lock:
            if task_id not in self._tasks:
                return False
            
            task_info = self._tasks[task_id]
            
            # 如果任务被停止，直接返回False
            if task_info['stop_event'].is_set():
                return False
            
            # 如果任务被暂停，等待恢复
            if task_info['pause_event'].is_set():
                logger.info(f"任务 {task_id} 被暂停，等待恢复...")
                # 等待暂停事件被清除（即恢复）或停止事件被设置
                while task_info['pause_event'].is_set() and not task_info['stop_event'].is_set():
                    # 使用更高效的等待方式，避免CPU占用过高
                    if not task_info['pause_event'].wait(timeout=1.0):
                        # 如果等待超时，重新检查状态
                        continue
                    break
                
                # 如果任务被停止，返回False
                if task_info['stop_event'].is_set():
                    logger.info(f"任务 {task_id} 在暂停期间被停止")
                    return False
                
                logger.info(f"任务 {task_id} 已恢复，继续执行")
            
            return True
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """获取任务状态"""
        with self._task_lock:
            if task_id not in self._tasks:
                return None
            return self._tasks[task_id]['status']
    
    def get_all_tasks(self) -> Dict[str, Dict]:
        """获取所有任务信息"""
        with self._task_lock:
            return self._tasks.copy()

# 全局任务管理器实例
task_manager = TaskManager()
