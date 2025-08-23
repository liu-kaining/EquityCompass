"""
股票池API
"""
from flask import Blueprint, request, session, jsonify
from app.utils.response import success_response, error_response
from app.services.data.stock_service import StockDataService
from app import db
import logging

logger = logging.getLogger(__name__)
stocks_api_bp = Blueprint('stocks_api', __name__)

def get_stock_service():
    """获取股票服务实例"""
    return StockDataService(db.session)

@stocks_api_bp.route('', methods=['GET'])
def get_stocks():
    """获取股票列表"""
    try:
        service = get_stock_service()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        market = request.args.get('market', '')
        
        # 获取股票池数据
        stock_pools = service.get_stock_pools()
        
        # 根据市场过滤
        if market == 'US':
            stocks = stock_pools['us_stocks']
        elif market == 'HK':
            stocks = stock_pools['hk_stocks']
        else:
            stocks = stock_pools['us_stocks'] + stock_pools['hk_stocks']
        
        # 分页处理
        start = (page - 1) * per_page
        end = start + per_page
        paginated_stocks = stocks[start:end]
        
        return success_response(data={
            'stocks': paginated_stocks,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(stocks),
                'pages': (len(stocks) + per_page - 1) // per_page
            },
            'summary': {
                'us_count': len(stock_pools['us_stocks']),
                'hk_count': len(stock_pools['hk_stocks']),
                'total_count': stock_pools['total_count']
            }
        })
        
    except Exception as e:
        logger.error(f"获取股票列表失败: {str(e)}")
        return error_response("获取股票列表失败", str(e))

@stocks_api_bp.route('/search', methods=['GET'])
def search_stocks():
    """搜索股票"""
    try:
        service = get_stock_service()
        
        # 获取查询参数
        keyword = request.args.get('q', '').strip()
        market = request.args.get('market', '')
        user_id = session.get('user_id')
        
        if not keyword:
            return error_response("搜索关键词不能为空")
        
        # 搜索股票
        stocks = service.search_stocks(keyword, market, user_id)
        
        return success_response(data={
            'stocks': stocks,
            'count': len(stocks),
            'keyword': keyword,
            'market': market
        })
        
    except Exception as e:
        logger.error(f"搜索股票失败: {str(e)}")
        return error_response("搜索股票失败", str(e))

@stocks_api_bp.route('', methods=['POST'])
def add_stock():
    """添加自定义股票"""
    try:
        # 检查用户登录状态
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空")
        
        code = data.get('code', '').strip().upper()
        name = data.get('name', '').strip()
        market = data.get('market', '').strip()
        
        # 验证必填字段
        if not code or not name or not market:
            return error_response("股票代码、名称和市场不能为空")
        
        if market not in ['US', 'HK']:
            return error_response("市场类型必须是 US 或 HK")
        
        service = get_stock_service()
        stock = service.add_custom_stock(code, name, market, user_id)
        
        return success_response(data=stock, message="股票添加成功")
        
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        logger.error(f"添加股票失败: {str(e)}")
        return error_response("添加股票失败", str(e))

@stocks_api_bp.route('/builtin', methods=['GET'])
def get_builtin_stocks():
    """获取内置股票池"""
    try:
        service = get_stock_service()
        stock_pools = service.get_stock_pools()
        
        return success_response(data={
            'us_stocks': stock_pools['us_stocks'],
            'hk_stocks': stock_pools['hk_stocks'],
            'summary': {
                'us_count': len(stock_pools['us_stocks']),
                'hk_count': len(stock_pools['hk_stocks']),
                'total_count': stock_pools['total_count']
            }
        })
        
    except Exception as e:
        logger.error(f"获取内置股票池失败: {str(e)}")
        return error_response("获取内置股票池失败", str(e))

@stocks_api_bp.route('/watchlist', methods=['GET'])
def get_watchlist():
    """获取用户关注列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        service = get_stock_service()
        watchlist_data = service.get_user_watchlist(user_id)
        
        return success_response(data=watchlist_data)
        
    except Exception as e:
        logger.error(f"获取关注列表失败: {str(e)}")
        return error_response("获取关注列表失败", str(e))

@stocks_api_bp.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """添加股票到关注列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空")
        
        stock_code = data.get('stock_code', '').strip().upper()
        if not stock_code:
            return error_response("股票代码不能为空")
        
        service = get_stock_service()
        result = service.add_to_watchlist(user_id, stock_code)
        
        if result['success']:
            return success_response(data=result, message=result['message'])
        else:
            return error_response(result['message'])
        
    except Exception as e:
        logger.error(f"添加关注失败: {str(e)}")
        return error_response("添加关注失败", str(e))

@stocks_api_bp.route('/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    """从关注列表移除股票"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空")
        
        stock_code = data.get('stock_code', '').strip().upper()
        if not stock_code:
            return error_response("股票代码不能为空")
        
        service = get_stock_service()
        result = service.remove_from_watchlist(user_id, stock_code)
        
        if result['success']:
            return success_response(data=result, message=result['message'])
        else:
            return error_response(result['message'])
        
    except Exception as e:
        logger.error(f"移除关注失败: {str(e)}")
        return error_response("移除关注失败", str(e))

@stocks_api_bp.route('/watchlist/clear', methods=['POST'])
def clear_watchlist():
    """一键清空关注列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        service = get_stock_service()
        result = service.clear_watchlist(user_id)
        
        if result['success']:
            return success_response(data=result, message=result['message'])
        else:
            return error_response(result['message'])
        
    except Exception as e:
        logger.error(f"清空关注列表失败: {str(e)}")
        return error_response("清空关注列表失败", str(e))

@stocks_api_bp.route('/<code>', methods=['GET'])
def get_stock_detail(code):
    """获取股票详情"""
    try:
        service = get_stock_service()
        stock = service.get_stock_by_code(code.upper())
        
        if not stock:
            return error_response("股票不存在", "NOT_FOUND")
        
        return success_response(data=stock)
        
    except Exception as e:
        logger.error(f"获取股票详情失败: {str(e)}")
        return error_response("获取股票详情失败", str(e))
