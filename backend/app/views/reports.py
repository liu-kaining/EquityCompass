"""
报告页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for, request
from datetime import datetime, timezone, timedelta

reports_bp = Blueprint('reports', __name__)

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def convert_to_beijing_time(utc_timestamp):
    """将UTC时间戳转换为北京时间（东八区）"""
    try:
        print(f"开始转换时间戳: {utc_timestamp}")
        
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
        print(f"转换结果: {result}")
        return result
    except Exception as e:
        print(f"时区转换失败: {utc_timestamp}, 错误: {str(e)}")
        return utc_timestamp  # 如果转换失败，返回原值

@reports_bp.route('/')
@login_required
def index():
    """报告列表页面"""
    from app.services.ai.analysis_service import AnalysisService
    from app import db
    
    # 获取用户ID
    user_id = session.get('user_id')
    
    # 获取查询参数
    stock_filter = request.args.get('stock', '')
    date_filter = request.args.get('date', '')
    analysis_type_filter = request.args.get('analysis_type', '')
    model_filter = request.args.get('model', '')
    
    # 获取分析服务
    analysis_service = AnalysisService(db.session)
    
    # 获取用户报告
    reports = analysis_service.get_user_reports(user_id, limit=50)
    
    # 应用筛选
    if stock_filter:
        reports = [r for r in reports if r.get('stock_code', '').upper() == stock_filter.upper()]
    
    if date_filter:
        if date_filter == 'today':
            from datetime import datetime
            today = datetime.utcnow().strftime('%Y-%m-%d')
            reports = [r for r in reports if r.get('date', '') == today]
    
    if analysis_type_filter:
        reports = [r for r in reports if r.get('analysis_type', '').lower() == analysis_type_filter.lower()]
    
    if model_filter:
        reports = [r for r in reports if r.get('provider', '').lower() == model_filter.lower()]
    
    # 格式化报告数据以匹配模板期望的结构
    formatted_reports = []
    available_stocks = set()  # 用于收集可用的股票
    
    for report in reports:
        # 转换时间戳
        metadata = report.get('metadata', {})
        if metadata and 'timestamp' in metadata:
            metadata['timestamp'] = convert_to_beijing_time(metadata['timestamp'])
        
        # 收集可用的股票
        stock_code = report.get('stock_code', '')
        stock_name = report.get('stock_name', '')
        if stock_code and stock_name:
            available_stocks.add((stock_code, stock_name))
        
        # 转换created_at时间戳
        created_at = report.get('created_at', report.get('date', ''))
        if created_at:
            created_at = convert_to_beijing_time(created_at)
        
        formatted_report = {
            'id': report.get('report_id', f"{report.get('stock_code', '')}_{report.get('date', '')}"),
            'stock_code': report.get('stock_code', ''),
            'stock_name': report.get('stock_name', ''),
            'ai_provider': report.get('ai_provider', report.get('provider', 'AI')),
            'analysis_type': report.get('analysis_type', 'fundamental'),
            'content': report.get('content', ''),
            'created_at': created_at,
            'analysis_date': report.get('analysis_date', ''),
            'provider': report.get('provider', 'AI'),
            'report_id': report.get('report_id', ''),
            'metadata': metadata
        }
        formatted_reports.append(formatted_report)
    
    # 转换为模板需要的格式
    available_stocks_list = [{'code': code, 'name': name} for code, name in sorted(available_stocks)]
    
    return render_template('reports/index.html', reports=formatted_reports, available_stocks=available_stocks_list)

@reports_bp.route('/<stock_code>')
@login_required
def detail(stock_code):
    """报告详情页面"""
    from app.services.ai.analysis_service import AnalysisService
    from app import db
    
    # 获取用户ID
    user_id = session.get('user_id')
    
    # 获取查询参数
    date = request.args.get('date', '')
    report_id = request.args.get('report_id', '')
    
    print(f"访问报告详情页面 - 股票代码: {stock_code}, 报告ID: {report_id}, 日期: {date}")
    
    # 获取分析服务
    analysis_service = AnalysisService(db.session)
    
    # 获取报告详情
    if report_id:
        # 如果指定了report_id，使用它来获取特定报告
        print(f"使用report_id获取报告: {report_id}")
        report = analysis_service.get_analysis_report(stock_code, date, report_id)
    else:
        # 否则获取最新的报告
        print(f"获取最新报告")
        report = analysis_service.get_analysis_report(stock_code, date)
    
    if not report:
        # 如果报告不存在，重定向到报告列表页面
        return redirect(url_for('reports.index'))
    
    # 转换时间戳
    metadata = report.get('metadata', {})
    print(f"原始metadata: {metadata}")
    if metadata and 'timestamp' in metadata:
        print(f"找到timestamp: {metadata['timestamp']}")
        metadata['timestamp'] = convert_to_beijing_time(metadata['timestamp'])
        print(f"转换后timestamp: {metadata['timestamp']}")
    else:
        print("没有找到timestamp字段")
    
    # 转换created_at时间戳
    created_at = report.get('created_at', '')
    if created_at:
        created_at = convert_to_beijing_time(created_at)
    
    # 格式化报告数据
    formatted_report = {
        'id': report.get('report_id', f"{report.get('stock_code', '')}_{report.get('analysis_date', '')}"),
        'stock_code': report.get('stock_code', ''),
        'stock_name': report.get('stock_name', ''),
        'market': report.get('market', ''),
        'analysis_date': report.get('analysis_date', ''),
        'content': report.get('content', ''),  # 保持原始内容，不进行HTML转义
        'provider': report.get('provider', 'AI'),
        'analysis_type': report.get('analysis_type', 'fundamental'),
        'created_at': created_at,
        'metadata': metadata
    }
    
    return render_template('reports/detail.html', report=formatted_report)
