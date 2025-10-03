"""
支付相关API接口
"""
from flask import Blueprint, request, jsonify, current_app, session
from sqlalchemy.orm import sessionmaker

from app.services.payment.payment_service import PaymentService, MockPaymentService
from app.services.coin.coin_service import CoinService
from app.utils.permissions import require_permission
from app.utils.response import success_response, error_response

# 创建蓝图
payment_bp = Blueprint('payment_api', __name__)

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


@payment_bp.route('/create', methods=['POST'])
@login_required
def create_payment():
    """创建支付订单"""
    try:
        data = request.get_json()
        if not data:
            return error_response("INVALID_REQUEST", "请求数据格式错误")
        
        order_id = data.get('order_id')
        payment_method = data.get('payment_method')
        
        if not order_id or not payment_method:
            return error_response("INVALID_PARAMETERS", "订单ID和支付方式不能为空")
        
        # 验证支付方式
        if payment_method not in ['ALIPAY', 'WECHAT', 'STRIPE']:
            return error_response("INVALID_PAYMENT_METHOD", "不支持的支付方式")
        
        db_session = get_db_session()
        
        # 检查是否为开发环境，使用模拟支付
        if current_app.config.get('ENV') == 'development':
            payment_service = MockPaymentService(db_session)
        else:
            payment_service = PaymentService(db_session)
        
        result = payment_service.create_payment_order(order_id, payment_method)
        return result
        
    except Exception as e:
        current_app.logger.error(f"创建支付订单失败: {str(e)}")
        return error_response("CREATE_PAYMENT_FAILED", "创建支付订单失败")


@payment_bp.route('/verify', methods=['POST'])
@login_required
def verify_payment():
    """验证支付结果"""
    try:
        data = request.get_json()
        if not data:
            return error_response("INVALID_REQUEST", "请求数据格式错误")
        
        payment_method = data.get('payment_method')
        payment_data = data.get('payment_data', {})
        
        if not payment_method:
            return error_response("INVALID_PARAMETERS", "支付方式不能为空")
        
        db_session = get_db_session()
        
        # 检查是否为开发环境，使用模拟支付
        if current_app.config.get('ENV') == 'development':
            payment_service = MockPaymentService(db_session)
        else:
            payment_service = PaymentService(db_session)
        
        result = payment_service.verify_payment(payment_method, payment_data)
        
        if result.get('success') and result.get('data', {}).get('verified'):
            # 支付验证成功，完成订单
            order_no = result.get('data', {}).get('order_no')
            if order_no:
                coin_service = CoinService(db_session)
                # 这里需要根据order_no找到order_id
                from app.models.coin import CoinOrder
                order = db_session.query(CoinOrder).filter(CoinOrder.order_no == order_no).first()
                if order:
                    complete_result = coin_service.complete_coin_order(
                        order.id, 
                        payment_method, 
                        payment_data.get('payment_id', order_no)
                    )
                    if complete_result.get('success'):
                        return success_response({
                            'verified': True,
                            'order_completed': True,
                            'coins_added': complete_result.get('data', {}).get('coins_added', 0)
                        })
        
        return result
        
    except Exception as e:
        current_app.logger.error(f"验证支付失败: {str(e)}")
        return error_response("VERIFY_PAYMENT_FAILED", "验证支付失败")


@payment_bp.route('/mock/success/<mock_payment_id>', methods=['POST'])
@login_required
def mock_payment_success(mock_payment_id):
    """模拟支付成功（仅开发环境）"""
    if current_app.config.get('ENV') != 'development':
        return error_response("NOT_ALLOWED", "仅开发环境可用")
    
    try:
        db_session = get_db_session()
        payment_service = MockPaymentService(db_session)
        
        result = payment_service.simulate_payment_success(mock_payment_id)
        
        if result.get('success') and result.get('data', {}).get('verified'):
            # 模拟支付成功，完成订单
            order_no = result.get('data', {}).get('order_no')
            if order_no:
                coin_service = CoinService(db_session)
                from app.models.coin import CoinOrder
                order = db_session.query(CoinOrder).filter(CoinOrder.order_no == order_no).first()
                if order:
                    complete_result = coin_service.complete_coin_order(
                        order.id, 
                        'MOCK', 
                        mock_payment_id
                    )
                    if complete_result.get('success'):
                        return success_response({
                            'verified': True,
                            'order_completed': True,
                            'coins_added': complete_result.get('data', {}).get('coins_added', 0),
                            'message': '模拟支付成功，金币已到账'
                        })
        
        return result
        
    except Exception as e:
        current_app.logger.error(f"模拟支付成功失败: {str(e)}")
        return error_response("MOCK_PAYMENT_FAILED", "模拟支付失败")


@payment_bp.route('/mock/failure/<mock_payment_id>', methods=['POST'])
@login_required
def mock_payment_failure(mock_payment_id):
    """模拟支付失败（仅开发环境）"""
    if current_app.config.get('ENV') != 'development':
        return error_response("NOT_ALLOWED", "仅开发环境可用")
    
    try:
        db_session = get_db_session()
        payment_service = MockPaymentService(db_session)
        
        result = payment_service.simulate_payment_failure(mock_payment_id)
        return result
        
    except Exception as e:
        current_app.logger.error(f"模拟支付失败: {str(e)}")
        return error_response("MOCK_PAYMENT_FAILED", "模拟支付失败")


@payment_bp.route('/methods', methods=['GET'])
def get_payment_methods():
    """获取支持的支付方式"""
    try:
        # 根据环境返回不同的支付方式
        if current_app.config.get('ENV') == 'development':
            methods = [
                {
                    'code': 'ALIPAY',
                    'name': '支付宝',
                    'icon': 'fab fa-alipay',
                    'color': '#1677ff',
                    'enabled': True,
                    'mock': True
                },
                {
                    'code': 'WECHAT',
                    'name': '微信支付',
                    'icon': 'fab fa-weixin',
                    'color': '#07c160',
                    'enabled': True,
                    'mock': True
                },
                {
                    'code': 'STRIPE',
                    'name': 'Stripe',
                    'icon': 'fab fa-stripe',
                    'color': '#635bff',
                    'enabled': True,
                    'mock': True
                }
            ]
        else:
            methods = [
                {
                    'code': 'ALIPAY',
                    'name': '支付宝',
                    'icon': 'fab fa-alipay',
                    'color': '#1677ff',
                    'enabled': True,
                    'mock': False
                },
                {
                    'code': 'WECHAT',
                    'name': '微信支付',
                    'icon': 'fab fa-weixin',
                    'color': '#07c160',
                    'enabled': True,
                    'mock': False
                },
                {
                    'code': 'STRIPE',
                    'name': 'Stripe',
                    'icon': 'fab fa-stripe',
                    'color': '#635bff',
                    'enabled': True,
                    'mock': False
                }
            ]
        
        return success_response({
            'payment_methods': methods
        })
        
    except Exception as e:
        current_app.logger.error(f"获取支付方式失败: {str(e)}")
        return error_response("GET_PAYMENT_METHODS_FAILED", "获取支付方式失败")


@payment_bp.route('/webhook/alipay', methods=['POST'])
def alipay_webhook():
    """支付宝支付回调"""
    try:
        data = request.form.to_dict()
        current_app.logger.info(f"支付宝回调数据: {data}")
        
        # 验证签名
        # 这里应该实现支付宝签名验证逻辑
        
        # 处理支付结果
        if data.get('trade_status') == 'TRADE_SUCCESS':
            order_no = data.get('out_trade_no')
            trade_no = data.get('trade_no')
            
            # 完成订单
            db_session = get_db_session()
            coin_service = CoinService(db_session)
            
            from app.models.coin import CoinOrder
            order = db_session.query(CoinOrder).filter(CoinOrder.order_no == order_no).first()
            if order and order.status == 'PENDING':
                complete_result = coin_service.complete_coin_order(
                    order.id, 
                    'ALIPAY', 
                    trade_no
                )
                if complete_result.get('success'):
                    return 'success'  # 支付宝要求返回success
        
        return 'fail'
        
    except Exception as e:
        current_app.logger.error(f"支付宝回调处理失败: {str(e)}")
        return 'fail'


@payment_bp.route('/webhook/wechat', methods=['POST'])
def wechat_webhook():
    """微信支付回调"""
    try:
        data = request.get_data()
        current_app.logger.info(f"微信支付回调数据: {data}")
        
        # 解析XML数据
        from app.services.payment.payment_service import PaymentService
        payment_service = PaymentService(get_db_session())
        result = payment_service._xml_to_dict(data.decode('utf-8'))
        
        # 验证签名
        # 这里应该实现微信支付签名验证逻辑
        
        # 处理支付结果
        if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
            order_no = result.get('out_trade_no')
            transaction_id = result.get('transaction_id')
            
            # 完成订单
            db_session = get_db_session()
            coin_service = CoinService(db_session)
            
            from app.models.coin import CoinOrder
            order = db_session.query(CoinOrder).filter(CoinOrder.order_no == order_no).first()
            if order and order.status == 'PENDING':
                complete_result = coin_service.complete_coin_order(
                    order.id, 
                    'WECHAT', 
                    transaction_id
                )
                if complete_result.get('success'):
                    # 返回成功响应
                    success_xml = payment_service._dict_to_xml({
                        'return_code': 'SUCCESS',
                        'return_msg': 'OK'
                    })
                    return success_xml, 200, {'Content-Type': 'application/xml'}
        
        # 返回失败响应
        fail_xml = payment_service._dict_to_xml({
            'return_code': 'FAIL',
            'return_msg': 'ERROR'
        })
        return fail_xml, 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        current_app.logger.error(f"微信支付回调处理失败: {str(e)}")
        fail_xml = payment_service._dict_to_xml({
            'return_code': 'FAIL',
            'return_msg': 'ERROR'
        })
        return fail_xml, 200, {'Content-Type': 'application/xml'}


@payment_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Stripe支付回调"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # 验证Stripe签名
        import stripe
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, current_app.config.get('STRIPE_WEBHOOK_SECRET')
            )
        except ValueError:
            return 'Invalid payload', 400
        except stripe.error.SignatureVerificationError:
            return 'Invalid signature', 400
        
        # 处理支付成功事件
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_no = payment_intent['metadata'].get('order_no')
            
            if order_no:
                # 完成订单
                db_session = get_db_session()
                coin_service = CoinService(db_session)
                
                from app.models.coin import CoinOrder
                order = db_session.query(CoinOrder).filter(CoinOrder.order_no == order_no).first()
                if order and order.status == 'PENDING':
                    complete_result = coin_service.complete_coin_order(
                        order.id, 
                        'STRIPE', 
                        payment_intent['id']
                    )
                    if complete_result.get('success'):
                        return 'OK', 200
        
        return 'OK', 200
        
    except Exception as e:
        current_app.logger.error(f"Stripe回调处理失败: {str(e)}")
        return 'Error', 500
