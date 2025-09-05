"""
分析页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime, timezone, timedelta
from app.services.data.stock_service import StockDataService
from app import db

analysis_bp = Blueprint('analysis', __name__)

def convert_to_beijing_time(utc_timestamp):
    """将UTC时间戳转换为北京时间（东八区）"""
    try:
        if isinstance(utc_timestamp, str):
            # 解析ISO格式的时间字符串
            # 如果时间字符串没有时区信息，假设为UTC时间
            if 'T' in utc_timestamp and ('+' in utc_timestamp or 'Z' in utc_timestamp):
                # 有时区信息的情况
                utc_time = datetime.fromisoformat(utc_timestamp.replace('Z', '+00:00'))
            else:
                # 没有时区信息，假设为UTC时间
                utc_time = datetime.fromisoformat(utc_timestamp)
                # 明确设置为UTC时区
                utc_time = utc_time.replace(tzinfo=timezone.utc)
        else:
            utc_time = utc_timestamp
            if utc_time.tzinfo is None:
                # 如果没有时区信息，假设为UTC时间
                utc_time = utc_time.replace(tzinfo=timezone.utc)
        
        # 转换为东八区
        beijing_tz = timezone(timedelta(hours=8))
        beijing_time = utc_time.astimezone(beijing_tz)
        
        result = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
        return result
    except Exception as e:
        return utc_timestamp  # 如果转换失败，返回原值

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@analysis_bp.route('/')
def index():
    """分析页面"""
    # 检查用户登录状态
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    # 获取用户关注列表
    service = StockDataService(db.session)
    watchlist_data = service.get_user_watchlist(user_id)
    
    return render_template('analysis/index.html', watchlist=watchlist_data['watchlist'])

@analysis_bp.route('/tasks')
@login_required
def tasks():
    """任务管理页面"""
    try:
        from flask import request
        from app.services.ai.analysis_service import AnalysisService
        
        user_id = session.get('user_id')
        # 确保user_id是整数类型
        if user_id:
            user_id = int(user_id)
        
        analysis_service = AnalysisService(db.session)
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 15, type=int)  # 每页显示15个任务
        
        # 获取用户的任务列表（不限制数量，用于分页）
        all_tasks = analysis_service.get_user_tasks(user_id, limit=1000)
        
        # 转换任务时间为东八区
        for task in all_tasks:
            if 'created_at' in task:
                task['created_at'] = convert_to_beijing_time(task['created_at'])
            if 'completed_at' in task:
                task['completed_at'] = convert_to_beijing_time(task['completed_at'])
        
        # 分页处理
        total_tasks = len(all_tasks)
        total_pages = (total_tasks + per_page - 1) // per_page
        
        # 确保页码在有效范围内
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1
        
        # 计算分页切片
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_tasks = all_tasks[start_idx:end_idx]
        
        # 构建分页信息
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_tasks,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
        
        return render_template('analysis/tasks.html', tasks=paginated_tasks, pagination=pagination)
        
    except Exception as e:
        print(f"ERROR: 任务管理页面异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('analysis/tasks.html', tasks=[], pagination=None)
