"""
股票管理页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for, request
from app.services.data.stock_service import StockDataService
from app import db

stocks_bp = Blueprint('stocks', __name__)

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_stock_service():
    """获取股票服务实例"""
    return StockDataService(db.session)

@stocks_bp.route('/')
@login_required
def index():
    """股票池页面"""
    try:
        service = get_stock_service()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        market = request.args.get('market', '')
        search = request.args.get('search', '')
        
        # 获取股票池数据
        stock_pools = service.get_stock_pools()
        
        # 根据市场过滤
        if market == 'US':
            stocks = stock_pools['us_stocks']
        elif market == 'HK':
            stocks = stock_pools['hk_stocks']
        else:
            stocks = stock_pools['us_stocks'] + stock_pools['hk_stocks']
        
        # 搜索过滤
        if search:
            filtered_stocks = []
            for stock in stocks:
                if (search.lower() in stock['code'].lower() or 
                    search.lower() in stock['name'].lower()):
                    filtered_stocks.append(stock)
            stocks = filtered_stocks
        
        # 分页处理
        total = len(stocks)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_stocks = stocks[start:end]
        
        # 获取用户关注列表
        user_id = session.get('user_id')
        watchlist_data = service.get_user_watchlist(user_id)
        watchlist_codes = {item['stock']['code'] for item in watchlist_data['watchlist']}
        
        # 标记已关注的股票
        for stock in paginated_stocks:
            stock['is_watching'] = stock['code'] in watchlist_codes
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'market': market,
            'search': search
        }
        
        watchlist_summary = {
            'count': len(watchlist_data['watchlist']),
            'remaining_slots': 20 - len(watchlist_data['watchlist']),
            'max_count': 20
        }
        
        return render_template('stocks/index.html', 
                             stocks=paginated_stocks,
                             pagination=pagination,
                             watchlist_summary=watchlist_summary)
                             
    except Exception as e:
        # 如果出错，返回空数据
        return render_template('stocks/index.html', 
                             stocks=[],
                             pagination={'page': 1, 'per_page': 20, 'total': 0, 'pages': 0, 'market': '', 'search': ''},
                             watchlist_summary={'count': 0, 'remaining_slots': 20, 'max_count': 20})

@stocks_bp.route('/watchlist')
@login_required
def watchlist():
    """关注列表页面"""
    try:
        service = get_stock_service()
        user_id = session.get('user_id')
        watchlist_data = service.get_user_watchlist(user_id)
        
        return render_template('stocks/watchlist.html', 
                             watchlist=watchlist_data['watchlist'],
                             summary=watchlist_data)
    except Exception as e:
        return render_template('stocks/watchlist.html', 
                             watchlist=[],
                             summary={'count': 0, 'remaining_slots': 20, 'max_count': 20})

@stocks_bp.route('/add')
@login_required
def add_custom():
    """添加自定义股票页面"""
    return render_template('stocks/add_custom.html')

@stocks_bp.route('/<code>')
@login_required
def detail(code):
    """股票详情页面"""
    try:
        service = get_stock_service()
        stock = service.get_stock_by_code(code.upper())
        
        if not stock:
            return render_template('stocks/detail.html', 
                                 stock=None, 
                                 stock_code=code,
                                 error="股票不存在")
        
        # 检查用户是否已关注
        user_id = session.get('user_id')
        watchlist_data = service.get_user_watchlist(user_id)
        watchlist_codes = {item['stock']['code'] for item in watchlist_data['watchlist']}
        stock['is_watching'] = stock['code'] in watchlist_codes
        
        # 获取关注列表统计信息
        watchlist_data = service.get_user_watchlist(user_id)
        watchlist_summary = {
            'count': len(watchlist_data['watchlist']),
            'remaining_slots': 20 - len(watchlist_data['watchlist']),
            'max_count': 20
        }
        
        return render_template('stocks/detail.html', 
                             stock=stock, 
                             stock_code=code,
                             watchlist_summary=watchlist_summary)
    except Exception as e:
        return render_template('stocks/detail.html', 
                             stock=None, 
                             stock_code=code,
                             error="获取股票信息失败",
                             watchlist_summary={'count': 0, 'remaining_slots': 20, 'max_count': 20})
