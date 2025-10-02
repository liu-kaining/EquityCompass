"""
金币系统视图
"""
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from sqlalchemy.orm import sessionmaker

from app.services.coin.coin_service import CoinService
from app.utils.permissions import require_permission
from app.utils.response import success_response, error_response

# 创建蓝图
coin_bp = Blueprint('coin', __name__)

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
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@coin_bp.route('/coin')
@login_required
def coin_center():
    """金币中心页面"""
    try:
        user_id = session.get('user_id')
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 获取用户金币信息
        coin_info_result = coin_service.get_user_coin_info(user_id)
        current_app.logger.info(f"coin_info_result type: {type(coin_info_result)}")
        if isinstance(coin_info_result, tuple):
            current_app.logger.info(f"coin_info_result[0] type: {type(coin_info_result[0])}")
            if hasattr(coin_info_result[0], 'get_json'):
                coin_info = coin_info_result[0].get_json()
            else:
                coin_info = coin_info_result[0]
        else:
            if hasattr(coin_info_result, 'get_json'):
                coin_info = coin_info_result.get_json()
            else:
                coin_info = coin_info_result
        
        # 获取金币套餐
        packages_result = coin_service.get_coin_packages()
        if isinstance(packages_result, tuple):
            if hasattr(packages_result[0], 'get_json'):
                packages = packages_result[0].get_json()
            else:
                packages = packages_result[0]
        else:
            if hasattr(packages_result, 'get_json'):
                packages = packages_result.get_json()
            else:
                packages = packages_result
        
        # 获取交易记录
        transactions_result = coin_service.get_user_transactions(user_id, page=1, per_page=10)
        if isinstance(transactions_result, tuple):
            if hasattr(transactions_result[0], 'get_json'):
                transactions = transactions_result[0].get_json()
            else:
                transactions = transactions_result[0]
        else:
            if hasattr(transactions_result, 'get_json'):
                transactions = transactions_result.get_json()
            else:
                transactions = transactions_result
        
        return render_template('coin/index.html',
                             coin_info=coin_info.get('data', {}),
                             packages=packages.get('data', []),
                             transactions=transactions.get('data', {}).get('transactions', []))
        
    except Exception as e:
        current_app.logger.error(f"加载金币中心失败: {str(e)}")
        return render_template('coin/index.html',
                             coin_info={},
                             packages=[],
                             transactions=[])


@coin_bp.route('/coin/transactions')
@login_required
def coin_transactions():
    """金币交易记录页面"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 获取交易记录
        user_id = session.get('user_id')
        result = coin_service.get_user_transactions(user_id, page, per_page)
        
        if result['success']:
            return render_template('coin/transactions.html',
                                 transactions=result['data']['transactions'],
                                 pagination=result['data']['pagination'])
        else:
            return render_template('coin/transactions.html',
                                 transactions=[],
                                 pagination={})
        
    except Exception as e:
        current_app.logger.error(f"加载交易记录失败: {str(e)}")
        return render_template('coin/transactions.html',
                             transactions=[],
                             pagination={})


@coin_bp.route('/coin/packages')
@login_required
def coin_packages():
    """金币套餐页面"""
    try:
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 获取金币套餐
        result = coin_service.get_coin_packages()
        
        if result['success']:
            return render_template('coin/packages.html',
                                 packages=result['data'])
        else:
            return render_template('coin/packages.html',
                                 packages=[])
        
    except Exception as e:
        current_app.logger.error(f"加载金币套餐失败: {str(e)}")
        return render_template('coin/packages.html',
                             packages=[])


# 管理员页面
@coin_bp.route('/admin/coin')
@login_required
@require_permission('SUPER_ADMIN')
def admin_coin_management():
    """金币管理页面（管理员）"""
    try:
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 获取金币系统统计
        # 这里可以添加统计方法
        
        return render_template('admin/coin_management.html',
                             statistics={})
        
    except Exception as e:
        current_app.logger.error(f"加载金币管理页面失败: {str(e)}")
        return render_template('admin/coin_management.html',
                             statistics={})


@coin_bp.route('/admin/coin/packages')
@login_required
@require_permission('SUPER_ADMIN')
def admin_coin_packages():
    """金币套餐管理页面（管理员）"""
    try:
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 获取所有套餐
        result = coin_service.get_coin_packages()
        
        if result['success']:
            return render_template('admin/coin_packages.html',
                                 packages=result['data'])
        else:
            return render_template('admin/coin_packages.html',
                                 packages=[])
        
    except Exception as e:
        current_app.logger.error(f"加载套餐管理页面失败: {str(e)}")
        return render_template('admin/coin_packages.html',
                             packages=[])


@coin_bp.route('/admin/coin/orders')
@login_required
@require_permission('SUPER_ADMIN')
def admin_coin_orders():
    """金币订单管理页面（管理员）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        db_session = get_db_session()
        coin_service = CoinService(db_session)
        
        # 获取所有订单
        # 这里可以添加获取所有订单的方法
        
        return render_template('admin/coin_orders.html',
                             orders=[],
                             pagination={})
        
    except Exception as e:
        current_app.logger.error(f"加载订单管理页面失败: {str(e)}")
        return render_template('admin/coin_orders.html',
                             orders=[],
                             pagination={})
