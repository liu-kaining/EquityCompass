"""
金币系统API端点
"""
from flask import Blueprint, request, jsonify, current_app, session
from sqlalchemy.orm import sessionmaker

from app.services.coin.coin_service import CoinService
from app.utils.permissions import require_permission
from app.utils.response import success_response, error_response

# 创建蓝图
coin_bp = Blueprint('coin_api', __name__)

# 数据库会话
def get_db_session():
    from app import db
    return db.session

def login_required(f):
    """登录验证装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return error_response("LOGIN_REQUIRED", "请先登录", 401)
        return f(*args, **kwargs)
    return decorated_function


@coin_bp.route('/info', methods=['GET'])
@login_required
def get_coin_info():
    """获取用户金币信息"""
    try:
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        user_id = session.get('user_id')
        result = coin_service.get_user_coin_info(user_id)
        return result
        
    except Exception as e:
        current_app.logger.error(f"获取金币信息失败: {str(e)}")
        return error_response("GET_COIN_INFO_FAILED", "获取金币信息失败")


@coin_bp.route('/daily-bonus-status', methods=['GET'])
@login_required
def daily_bonus_status():
    """检查每日签到状态"""
    try:
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        user_id = session.get('user_id')
        result = coin_service.check_daily_bonus_status(user_id)
        return result
        
    except Exception as e:
        current_app.logger.error(f"检查签到状态失败: {str(e)}")
        return error_response("CHECK_STATUS_FAILED", "检查签到状态失败")


@coin_bp.route('/bonus-stats', methods=['GET'])
@login_required
def get_bonus_stats():
    """获取签到统计"""
    try:
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        user_id = session.get('user_id')
        result = coin_service.get_bonus_stats(user_id)
        return result
        
    except Exception as e:
        current_app.logger.error(f"获取签到统计失败: {str(e)}")
        return error_response("GET_BONUS_STATS_FAILED", "获取签到统计失败")


@coin_bp.route('/daily-bonus', methods=['POST'])
@login_required
def daily_bonus():
    """每日签到奖励"""
    try:
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        user_id = session.get('user_id')
        current_app.logger.info(f"每日签到请求 - user_id: {user_id}")
        
        result = coin_service.daily_bonus(user_id)
        current_app.logger.info(f"每日签到结果: {result}")
        return result
        
    except Exception as e:
        current_app.logger.error(f"每日签到失败: {str(e)}", exc_info=True)
        return error_response("DAILY_BONUS_FAILED", "每日签到失败")


@coin_bp.route('/packages', methods=['GET'])
def get_coin_packages():
    """获取金币套餐列表"""
    try:
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        result = coin_service.get_coin_packages()
        return result
        
    except Exception as e:
        current_app.logger.error(f"获取金币套餐失败: {str(e)}")
        return error_response("GET_PACKAGES_FAILED", "获取金币套餐失败")


@coin_bp.route('/order', methods=['POST'])
@login_required
def create_coin_order():
    """创建金币订单"""
    try:
        data = request.get_json()
        package_id = data.get('package_id')
        
        if not package_id:
            return error_response("INVALID_PARAMETERS", "套餐ID不能为空")
        
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        user_id = session.get('user_id')
        result = coin_service.create_coin_order(user_id, package_id)
        return result
        
    except Exception as e:
        current_app.logger.error(f"创建订单失败: {str(e)}")
        return error_response("CREATE_ORDER_FAILED", "创建订单失败")


@coin_bp.route('/order/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_coin_order(order_id):
    """完成金币订单（支付成功）"""
    try:
        data = request.get_json()
        payment_method = data.get('payment_method')
        payment_id = data.get('payment_id')
        
        if not payment_method or not payment_id:
            return error_response("INVALID_PARAMETERS", "支付信息不完整")
        
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        result = coin_service.complete_coin_order(order_id, payment_method, payment_id)
        return result
        
    except Exception as e:
        current_app.logger.error(f"完成订单失败: {str(e)}")
        return error_response("COMPLETE_ORDER_FAILED", "完成订单失败")


@coin_bp.route('/transactions', methods=['GET'])
@login_required
def get_coin_transactions():
    """获取用户交易记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        user_id = session.get('user_id')
        result = coin_service.get_user_transactions(user_id, page, per_page)
        return result
        
    except Exception as e:
        current_app.logger.error(f"获取交易记录失败: {str(e)}")
        return error_response("GET_TRANSACTIONS_FAILED", "获取交易记录失败")


@coin_bp.route('/spend', methods=['POST'])
@login_required
def spend_coins():
    """消耗金币（内部API，用于分析服务）"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        description = data.get('description')
        related_id = data.get('related_id')
        related_type = data.get('related_type')
        
        if not amount or not description:
            return error_response("INVALID_PARAMETERS", "参数不完整")
        
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        user_id = session.get('user_id')
        result = coin_service.spend_coins(
            user_id=user_id,
            amount=amount,
            description=description,
            related_id=related_id,
            related_type=related_type
        )
        return result
        
    except Exception as e:
        current_app.logger.error(f"消耗金币失败: {str(e)}")
        return error_response("SPEND_COINS_FAILED", "消耗金币失败")


# 管理员API
@coin_bp.route('/admin/statistics', methods=['GET'])
@login_required
@require_permission('SUPER_ADMIN')
def get_coin_statistics():
    """获取金币系统统计（管理员）"""
    try:
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 这里可以添加统计方法
        result = success_response({"message": "统计功能待实现"})
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"获取统计信息失败: {str(e)}")
        return error_response("GET_STATISTICS_FAILED", "获取统计信息失败")


@coin_bp.route('/admin/packages', methods=['POST'])
@login_required
@require_permission('SUPER_ADMIN')
def create_coin_package():
    """创建金币套餐（管理员）"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'coins', 'price', 'package_type']
        for field in required_fields:
            if field not in data:
                return error_response("MISSING_FIELD", f"缺少必要字段: {field}")
        
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 这里可以添加创建套餐的方法
        result = success_response({"message": "创建套餐功能待实现"})
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"创建套餐失败: {str(e)}")
        return error_response("CREATE_PACKAGE_FAILED", "创建套餐失败")


@coin_bp.route('/admin/packages/<int:package_id>', methods=['PUT'])
@login_required
@require_permission('SUPER_ADMIN')
def update_coin_package(package_id):
    """更新金币套餐（管理员）"""
    try:
        data = request.get_json()
        
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 这里可以添加更新套餐的方法
        result = success_response({"message": "更新套餐功能待实现"})
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"更新套餐失败: {str(e)}")
        return error_response("UPDATE_PACKAGE_FAILED", "更新套餐失败")


@coin_bp.route('/admin/orders', methods=['GET'])
@login_required
@require_permission('SUPER_ADMIN')
def get_all_coin_orders():
    """获取所有金币订单（管理员）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 这里可以添加获取所有订单的方法
        result = success_response({"message": "获取订单功能待实现"})
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"获取订单失败: {str(e)}")
        return error_response("GET_ORDERS_FAILED", "获取订单失败")
