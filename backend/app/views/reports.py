"""
报告页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, send_file
from datetime import datetime, timezone, timedelta
import tempfile
import os
import re
import markdown
import zipfile
import io
from playwright.sync_api import sync_playwright
from app.services.ai.analysis_service import AnalysisService

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
    from app import db
    
    # 获取用户ID
    user_id = session.get('user_id')
    
    # 获取查询参数
    stock_filter = request.args.get('stock', '')
    date_filter = request.args.get('date', '')
    analysis_type_filter = request.args.get('analysis_type', '')
    model_filter = request.args.get('model', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)  # 每页显示12个报告
    
    # 获取分析服务
    analysis_service = AnalysisService(db.session)
    
    # 获取用户报告（不限制数量，用于筛选）
    all_reports = analysis_service.get_user_reports(user_id, limit=1000)
    
    # 应用筛选
    if stock_filter:
        all_reports = [r for r in all_reports if r.get('stock_code', '').upper() == stock_filter.upper()]
    
    if date_filter:
        if date_filter == 'today':
            from datetime import datetime
            today = datetime.utcnow().strftime('%Y-%m-%d')
            all_reports = [r for r in all_reports if r.get('date', '') == today]
    
    if analysis_type_filter:
        all_reports = [r for r in all_reports if r.get('analysis_type', '').lower() == analysis_type_filter.lower()]
    
    if model_filter:
        all_reports = [r for r in all_reports if r.get('provider', '').lower() == model_filter.lower()]
    
    # 格式化报告数据以匹配模板期望的结构
    formatted_reports = []
    available_stocks = set()  # 用于收集可用的股票
    
    for report in all_reports:
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
    
    # 分页处理
    total_reports = len(formatted_reports)
    total_pages = (total_reports + per_page - 1) // per_page
    
    # 确保页码在有效范围内
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    
    # 计算分页切片
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_reports = formatted_reports[start_idx:end_idx]
    
    # 构建分页信息
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_reports,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None
    }
    
    return render_template('reports/index.html', 
                         reports=paginated_reports, 
                         available_stocks=available_stocks_list,
                         pagination=pagination,
                         max=max,
                         min=min)

@reports_bp.route('/<stock_code>')
@login_required
def detail(stock_code):
    """报告详情页面"""
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
    report_id = report.get('report_id', f"{report.get('stock_code', '')}_{report.get('analysis_date', '')}")
    print(f"报告ID: {report_id}")
    print(f"报告数据: {report}")
    
    formatted_report = {
        'id': report_id,
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
    
    # 获取同一公司的历史报告（排除当前报告）
    historical_reports = []
    try:
        all_reports = analysis_service.get_all_reports_for_stock(stock_code)
        current_report_id = report.get('report_id', '')
        
        for hist_report in all_reports:
            # 排除当前报告
            if hist_report.get('report_id') != current_report_id:
                # 转换时间戳
                hist_metadata = hist_report.get('metadata', {})
                if hist_metadata and 'timestamp' in hist_metadata:
                    hist_metadata['timestamp'] = convert_to_beijing_time(hist_metadata['timestamp'])
                
                hist_created_at = hist_report.get('created_at', '')
                if hist_created_at:
                    hist_created_at = convert_to_beijing_time(hist_created_at)
                
                formatted_hist_report = {
                    'id': hist_report.get('report_id', f"{hist_report.get('stock_code', '')}_{hist_report.get('analysis_date', '')}"),
                    'stock_code': hist_report.get('stock_code', ''),
                    'stock_name': hist_report.get('stock_name', ''),
                    'analysis_date': hist_report.get('analysis_date', ''),
                    'provider': hist_report.get('provider', 'AI'),
                    'analysis_type': hist_report.get('analysis_type', 'fundamental'),
                    'created_at': hist_created_at,
                    'metadata': hist_metadata
                }
                historical_reports.append(formatted_hist_report)
        
        # 按创建时间倒序排列，最新的在前面
        historical_reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # 只显示最近5个历史报告
        historical_reports = historical_reports[:5]
        
    except Exception as e:
        print(f"获取历史报告时出错: {e}")
        historical_reports = []
    
    return render_template('reports/detail.html', report=formatted_report, historical_reports=historical_reports)

@reports_bp.route('/<stock_code>/export-pdf')
@login_required
def export_pdf(stock_code):
    """导出报告为PDF"""
    from app import db
    
    # 获取用户ID
    user_id = session.get('user_id')
    
    # 获取查询参数
    date = request.args.get('date', '')
    report_id = request.args.get('report_id', '')
    
    # 获取分析服务
    analysis_service = AnalysisService(db.session)
    
    # 获取报告详情
    if report_id:
        report = analysis_service.get_analysis_report(stock_code, date, report_id)
    else:
        report = analysis_service.get_analysis_report(stock_code, date)
    
    if not report:
        return jsonify({'success': False, 'error': '报告不存在'})
    
    # 转换时间戳
    metadata = report.get('metadata', {})
    if metadata and 'timestamp' in metadata:
        metadata['timestamp'] = convert_to_beijing_time(metadata['timestamp'])
    
    created_at = report.get('created_at', '')
    if created_at:
        created_at = convert_to_beijing_time(created_at)
    
    try:
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        # 生成HTML内容，保持网页的漂亮样式
        analysis_type_text = '基本面分析' if report.get('analysis_type') == 'fundamental' else '技术面分析'
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{report.get('stock_code', '')} - {report.get('stock_name', '')} 分析报告</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                    @bottom-center {{
                        content: "由 EquityCompass AI 分析平台生成";
                        font-size: 10px;
                        color: #666;
                    }}
                }}
                
                body {{
                    font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #4f46e5;
                }}
                
                .title {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #4f46e5;
                    margin-bottom: 10px;
                }}
                
                .subtitle {{
                    font-size: 16px;
                    color: #666;
                }}
                
                .info-section {{
                    margin-bottom: 30px;
                }}
                
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                
                .info-item {{
                    padding: 12px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    border-left: 4px solid #4f46e5;
                }}
                
                .info-label {{
                    font-weight: bold;
                    color: #4f46e5;
                    display: block;
                    margin-bottom: 5px;
                }}
                
                .info-value {{
                    color: #333;
                }}
                
                .content {{
                    margin-top: 30px;
                }}
                
                .content h1, .content h2, .content h3 {{
                    color: #4f46e5;
                    margin-top: 25px;
                    margin-bottom: 15px;
                    font-weight: bold;
                }}
                
                .content h1 {{
                    font-size: 20px;
                }}
                
                .content h2 {{
                    font-size: 18px;
                }}
                
                .content h3 {{
                    font-size: 16px;
                }}
                
                .content p {{
                    margin-bottom: 15px;
                    text-align: justify;
                }}
                
                .content ul, .content ol {{
                    margin-bottom: 15px;
                    padding-left: 25px;
                }}
                
                .content li {{
                    margin-bottom: 8px;
                }}
                
                .content strong {{
                    color: #4f46e5;
                    font-weight: bold;
                }}
                
                .content code {{
                    background: #f1f3f4;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                }}
                
                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    border-top: 1px solid #eee;
                    padding-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">股票分析报告</div>
                <div class="subtitle">AI驱动的智能投资分析</div>
            </div>
            
            <div class="info-section">
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">股票代码</span>
                        <span class="info-value">{report.get('stock_code', '')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">公司名称</span>
                        <span class="info-value">{report.get('stock_name', '')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">分析日期</span>
                        <span class="info-value">{report.get('analysis_date', '')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">AI模型</span>
                        <span class="info-value">{report.get('provider', '')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">市场</span>
                        <span class="info-value">{report.get('market', '')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">分析类型</span>
                        <span class="info-value">{analysis_type_text}</span>
                    </div>
                </div>
            </div>
            
            <div class="content">
                {markdown.markdown(report.get('content', ''), extensions=['fenced_code', 'tables', 'nl2br'])}
            </div>
            
            <div class="footer">
                <p>本报告由 EquityCompass AI 分析平台生成</p>
                <p>生成时间：{created_at or metadata.get('timestamp', '')}</p>
            </div>
        </body>
        </html>
        """
        
        # 使用playwright生成PDF
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content)
            page.pdf(path=pdf_path, format='A4', margin={'top': '2cm', 'right': '2cm', 'bottom': '2cm', 'left': '2cm'})
            browser.close()
        
        # 生成文件名
        filename = f"{report.get('stock_code', '')}_{report.get('analysis_date', '')}_分析报告.pdf"
        
        # 返回PDF文件
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'PDF生成失败: {str(e)}'})
    finally:
        # 清理临时文件
        if 'pdf_path' in locals() and os.path.exists(pdf_path):
            os.unlink(pdf_path)

@reports_bp.route('/batch-export', methods=['POST'])
@login_required
def batch_export():
    """批量导出报告为ZIP文件"""
    from app import db
    
    # 获取用户ID
    user_id = session.get('user_id')
    
    # 获取请求数据
    data = request.get_json()
    reports_data = data.get('reports', [])
    
    if not reports_data:
        return jsonify({'success': False, 'error': '没有选择任何报告'})
    
    # 获取分析服务
    analysis_service = AnalysisService(db.session)
    
    # 创建内存中的ZIP文件
    zip_buffer = io.BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for report_info in reports_data:
                stock_code = report_info.get('stock_code')
                report_id = report_info.get('report_id')
                
                # 获取报告详情
                report = analysis_service.get_analysis_report(stock_code, '', report_id)
                
                if not report:
                    continue
                
                # 转换时间戳
                metadata = report.get('metadata', {})
                if metadata and 'timestamp' in metadata:
                    metadata['timestamp'] = convert_to_beijing_time(metadata['timestamp'])
                
                created_at = report.get('created_at', '')
                if created_at:
                    created_at = convert_to_beijing_time(created_at)
                
                # 生成HTML内容
                analysis_type_text = '基本面分析' if report.get('analysis_type') == 'fundamental' else '技术面分析'
                
                html_content = f"""
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{report.get('stock_code', '')} - {report.get('stock_name', '')} 分析报告</title>
                    <style>
                        @page {{
                            size: A4;
                            margin: 2cm;
                            @bottom-center {{
                                content: "由 EquityCompass AI 分析平台生成";
                                font-size: 10px;
                                color: #666;
                            }}
                        }}
                        
                        body {{
                            font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            margin: 0;
                            padding: 0;
                        }}
                        
                        .header {{
                            text-align: center;
                            margin-bottom: 30px;
                            padding-bottom: 20px;
                            border-bottom: 2px solid #4f46e5;
                        }}
                        
                        .title {{
                            font-size: 28px;
                            font-weight: bold;
                            color: #4f46e5;
                            margin-bottom: 10px;
                        }}
                        
                        .subtitle {{
                            font-size: 16px;
                            color: #666;
                        }}
                        
                        .info-section {{
                            margin-bottom: 30px;
                        }}
                        
                        .info-grid {{
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: 15px;
                            margin-bottom: 20px;
                        }}
                        
                        .info-item {{
                            padding: 12px;
                            background: #f8f9fa;
                            border-radius: 8px;
                            border-left: 4px solid #4f46e5;
                        }}
                        
                        .info-label {{
                            font-weight: bold;
                            color: #4f46e5;
                            display: block;
                            margin-bottom: 5px;
                        }}
                        
                        .info-value {{
                            color: #333;
                        }}
                        
                        .content {{
                            margin-top: 30px;
                        }}
                        
                        .content h1, .content h2, .content h3 {{
                            color: #4f46e5;
                            margin-top: 25px;
                            margin-bottom: 15px;
                            font-weight: bold;
                        }}
                        
                        .content h1 {{
                            font-size: 20px;
                        }}
                        
                        .content h2 {{
                            font-size: 18px;
                        }}
                        
                        .content h3 {{
                            font-size: 16px;
                        }}
                        
                        .content p {{
                            margin-bottom: 15px;
                            text-align: justify;
                        }}
                        
                        .content ul, .content ol {{
                            margin-bottom: 15px;
                            padding-left: 25px;
                        }}
                        
                        .content li {{
                            margin-bottom: 8px;
                        }}
                        
                        .content strong {{
                            color: #4f46e5;
                            font-weight: bold;
                        }}
                        
                        .content code {{
                            background: #f1f3f4;
                            padding: 2px 6px;
                            border-radius: 4px;
                            font-family: 'Courier New', monospace;
                        }}
                        
                        .footer {{
                            margin-top: 40px;
                            text-align: center;
                            font-size: 12px;
                            color: #999;
                            border-top: 1px solid #eee;
                            padding-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <div class="title">股票分析报告</div>
                        <div class="subtitle">AI驱动的智能投资分析</div>
                    </div>
                    
                    <div class="info-section">
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="info-label">股票代码</span>
                                <span class="info-value">{report.get('stock_code', '')}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">公司名称</span>
                                <span class="info-value">{report.get('stock_name', '')}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">分析日期</span>
                                <span class="info-value">{report.get('analysis_date', '')}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">AI模型</span>
                                <span class="info-value">{report.get('provider', '')}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">市场</span>
                                <span class="info-value">{report.get('market', '')}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">分析类型</span>
                                <span class="info-value">{analysis_type_text}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="content">
                        {markdown.markdown(report.get('content', ''), extensions=['fenced_code', 'tables', 'nl2br'])}
                    </div>
                    
                    <div class="footer">
                        <p>本报告由 EquityCompass AI 分析平台生成</p>
                        <p>生成时间：{created_at or metadata.get('timestamp', '')}</p>
                    </div>
                </body>
                </html>
                """
                
                # 创建临时PDF文件
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    pdf_path = tmp_file.name
                
                try:
                    # 使用playwright生成PDF
                    with sync_playwright() as p:
                        browser = p.chromium.launch()
                        page = browser.new_page()
                        page.set_content(html_content)
                        page.pdf(path=pdf_path, format='A4', margin={'top': '2cm', 'right': '2cm', 'bottom': '2cm', 'left': '2cm'})
                        browser.close()
                    
                    # 生成文件名
                    filename = f"{report.get('stock_code', '')}_{report.get('analysis_date', '')}_分析报告.pdf"
                    
                    # 将PDF添加到ZIP文件
                    with open(pdf_path, 'rb') as pdf_file:
                        zip_file.writestr(filename, pdf_file.read())
                        
                finally:
                    # 清理临时PDF文件
                    if os.path.exists(pdf_path):
                        os.unlink(pdf_path)
        
        # 重置缓冲区位置
        zip_buffer.seek(0)
        
        # 返回ZIP文件
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"分析报告_{datetime.now().strftime('%Y-%m-%d')}.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'批量导出失败: {str(e)}'})
