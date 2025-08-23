"""
时区处理工具
"""
from datetime import datetime, timezone, timedelta
from flask import current_app


def utc_to_local(utc_time: datetime) -> datetime:
    """将UTC时间转换为本地时间（东八区）"""
    if not utc_time:
        return None
    
    # 确保时间是UTC时区
    if utc_time.tzinfo is None:
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    
    # 转换为东八区
    local_tz = timezone(timedelta(hours=8))
    return utc_time.astimezone(local_tz)


def local_to_utc(local_time: datetime) -> datetime:
    """将本地时间转换为UTC时间"""
    if not local_time:
        return None
    
    # 确保时间是本地时区
    if local_time.tzinfo is None:
        local_tz = timezone(timedelta(hours=8))
        local_time = local_time.replace(tzinfo=local_tz)
    
    # 转换为UTC
    return local_time.astimezone(timezone.utc)


def format_local_time(dt: datetime, format_str: str = '%Y-%m-%d %H:%M') -> str:
    """格式化本地时间显示"""
    if not dt:
        return None
    
    local_time = utc_to_local(dt) if dt.tzinfo is None or dt.tzinfo == timezone.utc else dt
    return local_time.strftime(format_str)


def get_current_local_time() -> datetime:
    """获取当前本地时间"""
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utc_to_local(utc_now)
