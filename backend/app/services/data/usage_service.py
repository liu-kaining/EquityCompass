"""
用户使用量跟踪服务
"""
import os
import json
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class UsageTrackingService:
    """用户使用量跟踪服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.usage_dir = 'data/usage'
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保目录存在"""
        os.makedirs('data', exist_ok=True)
        os.makedirs(self.usage_dir, exist_ok=True)
    
    def _get_today_usage_file(self, user_id: int) -> str:
        """获取今天的使用量文件路径"""
        today = date.today().strftime('%Y-%m-%d')
        return os.path.join(self.usage_dir, f"user_{user_id}_{today}.json")
    
    def get_today_usage(self, user_id: int) -> Dict[str, Any]:
        """获取用户今日使用量"""
        try:
            usage_file = self._get_today_usage_file(user_id)
            
            if not os.path.exists(usage_file):
                return {
                    'user_id': user_id,
                    'date': date.today().strftime('%Y-%m-%d'),
                    'analysis_count': 0,
                    'last_analysis_time': None
                }
            
            with open(usage_file, 'r', encoding='utf-8') as f:
                usage_data = json.load(f)
            
            return usage_data
            
        except Exception as e:
            logger.error(f"获取用户今日使用量失败: {str(e)}")
            return {
                'user_id': user_id,
                'date': date.today().strftime('%Y-%m-%d'),
                'analysis_count': 0,
                'last_analysis_time': None
            }
    
    def increment_analysis_count(self, user_id: int) -> Dict[str, Any]:
        """增加分析次数"""
        try:
            usage_data = self.get_today_usage(user_id)
            usage_data['analysis_count'] += 1
            usage_data['last_analysis_time'] = datetime.now().isoformat()
            
            # 保存到文件
            usage_file = self._get_today_usage_file(user_id)
            with open(usage_file, 'w', encoding='utf-8') as f:
                json.dump(usage_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"用户 {user_id} 今日分析次数已增加到 {usage_data['analysis_count']}")
            return usage_data
            
        except Exception as e:
            logger.error(f"增加分析次数失败: {str(e)}")
            raise e
    
    def check_daily_limit(self, user_id: int, daily_limit: int = 10) -> Dict[str, Any]:
        """检查是否超过每日限制"""
        try:
            usage_data = self.get_today_usage(user_id)
            current_count = usage_data['analysis_count']
            
            return {
                'user_id': user_id,
                'current_count': current_count,
                'daily_limit': daily_limit,
                'remaining': max(0, daily_limit - current_count),
                'can_analyze': current_count < daily_limit,
                'is_limit_reached': current_count >= daily_limit
            }
            
        except Exception as e:
            logger.error(f"检查每日限制失败: {str(e)}")
            return {
                'user_id': user_id,
                'current_count': 0,
                'daily_limit': daily_limit,
                'remaining': daily_limit,
                'can_analyze': True,
                'is_limit_reached': False
            }
    
    def get_usage_stats(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """获取用户使用统计（最近N天）"""
        try:
            stats = {
                'user_id': user_id,
                'total_analyses': 0,
                'daily_breakdown': [],
                'average_daily': 0
            }
            
            from datetime import timedelta
            
            for i in range(days):
                check_date = date.today() - timedelta(days=i)
                date_str = check_date.strftime('%Y-%m-%d')
                
                usage_file = os.path.join(self.usage_dir, f"user_{user_id}_{date_str}.json")
                
                if os.path.exists(usage_file):
                    with open(usage_file, 'r', encoding='utf-8') as f:
                        day_data = json.load(f)
                        day_count = day_data.get('analysis_count', 0)
                else:
                    day_count = 0
                
                stats['daily_breakdown'].append({
                    'date': date_str,
                    'count': day_count
                })
                stats['total_analyses'] += day_count
            
            stats['average_daily'] = round(stats['total_analyses'] / days, 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"获取使用统计失败: {str(e)}")
            return {
                'user_id': user_id,
                'total_analyses': 0,
                'daily_breakdown': [],
                'average_daily': 0
            }
