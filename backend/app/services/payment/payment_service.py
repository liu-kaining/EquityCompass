"""
支付服务
支持多种支付方式：支付宝、微信支付、Stripe等
"""
import os
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from urllib.parse import urlencode

import requests
from flask import current_app

from app.models.coin import CoinOrder, CoinPackage
from app.models.payment import PaymentTransaction
from app.utils.response import success_response, error_response, service_success_response, service_error_response


class PaymentService:
    """支付服务基类"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.config = {
            'alipay': {
                'app_id': os.getenv('ALIPAY_APP_ID'),
                'private_key': os.getenv('ALIPAY_PRIVATE_KEY'),
                'public_key': os.getenv('ALIPAY_PUBLIC_KEY'),
                'gateway_url': os.getenv('ALIPAY_GATEWAY_URL', 'https://openapi.alipay.com/gateway.do'),
                'notify_url': os.getenv('ALIPAY_NOTIFY_URL', 'https://yourdomain.com/api/payment/alipay/notify'),
                'return_url': os.getenv('ALIPAY_RETURN_URL', 'https://yourdomain.com/payment/success')
            },
            'wechat': {
                'app_id': os.getenv('WECHAT_APP_ID'),
                'mch_id': os.getenv('WECHAT_MCH_ID'),
                'api_key': os.getenv('WECHAT_API_KEY'),
                'notify_url': os.getenv('WECHAT_NOTIFY_URL', 'https://yourdomain.com/api/payment/wechat/notify'),
                'gateway_url': 'https://api.mch.weixin.qq.com/pay/unifiedorder'
            },
            'stripe': {
                'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY'),
                'secret_key': os.getenv('STRIPE_SECRET_KEY'),
                'webhook_secret': os.getenv('STRIPE_WEBHOOK_SECRET')
            }
        }
    
    def create_payment_order(self, order_id: int, payment_method: str) -> Dict:
        """创建支付订单"""
        try:
            # 获取订单信息
            order = self.db.query(CoinOrder).filter(CoinOrder.id == order_id).first()
            if not order:
                return service_error_response("ORDER_NOT_FOUND", "订单不存在")
            
            if order.status != 'PENDING':
                return service_error_response("INVALID_ORDER_STATUS", "订单状态不正确")
            
            # 根据支付方式创建支付订单
            if payment_method == 'ALIPAY':
                return self._create_alipay_order(order)
            elif payment_method == 'WECHAT':
                return self._create_wechat_order(order)
            elif payment_method == 'STRIPE':
                return self._create_stripe_order(order)
            else:
                return service_error_response("UNSUPPORTED_PAYMENT_METHOD", "不支持的支付方式")
                
        except Exception as e:
            current_app.logger.error(f"创建支付订单失败: {str(e)}")
            return service_error_response("CREATE_PAYMENT_ORDER_FAILED", "创建支付订单失败")
    
    def _create_alipay_order(self, order: CoinOrder) -> Dict:
        """创建支付宝订单"""
        try:
            import alipay_sdk_python
            
            # 初始化支付宝SDK
            alipay = alipay_sdk_python.Alipay(
                appid=self.config['alipay']['app_id'],
                app_notify_url=self.config['alipay']['notify_url'],
                app_private_key_string=self.config['alipay']['private_key'],
                alipay_public_key_string=self.config['alipay']['public_key'],
                sign_type="RSA2",
                debug=False
            )
            
            # 构建订单参数
            order_string = alipay.api_alipay_trade_page_pay(
                out_trade_no=order.order_no,
                total_amount=str(order.amount),
                subject=f"购买{order.package.name}",
                return_url=self.config['alipay']['return_url'],
                notify_url=self.config['alipay']['notify_url']
            )
            
            # 生成支付URL
            pay_url = f"{self.config['alipay']['gateway_url']}?{order_string}"
            
            return service_success_response({
                'payment_url': pay_url,
                'order_no': order.order_no,
                'amount': order.amount,
                'payment_method': 'ALIPAY'
            })
            
        except ImportError:
            # 如果没有安装支付宝SDK，返回模拟支付URL
            return self._create_mock_payment_order(order, 'ALIPAY')
        except Exception as e:
            current_app.logger.error(f"创建支付宝订单失败: {str(e)}")
            return service_error_response("ALIPAY_ORDER_FAILED", "创建支付宝订单失败")
    
    def _create_wechat_order(self, order: CoinOrder) -> Dict:
        """创建微信支付订单"""
        try:
            # 构建微信支付参数
            params = {
                'appid': self.config['wechat']['app_id'],
                'mch_id': self.config['wechat']['mch_id'],
                'nonce_str': self._generate_nonce_str(),
                'body': f"购买{order.package.name}",
                'out_trade_no': order.order_no,
                'total_fee': int(order.amount * 100),  # 微信支付金额单位为分
                'spbill_create_ip': '127.0.0.1',
                'notify_url': self.config['wechat']['notify_url'],
                'trade_type': 'NATIVE'
            }
            
            # 生成签名
            params['sign'] = self._generate_wechat_sign(params)
            
            # 发送请求到微信支付
            xml_data = self._dict_to_xml(params)
            response = requests.post(
                self.config['wechat']['gateway_url'],
                data=xml_data,
                headers={'Content-Type': 'application/xml'}
            )
            
            # 解析响应
            result = self._xml_to_dict(response.text)
            
            if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
                return service_success_response({
                    'qr_code': result.get('code_url'),
                    'order_no': order.order_no,
                    'amount': order.amount,
                    'payment_method': 'WECHAT'
                })
            else:
                return service_error_response("WECHAT_ORDER_FAILED", f"微信支付失败: {result.get('return_msg', '未知错误')}")
                
        except Exception as e:
            current_app.logger.error(f"创建微信支付订单失败: {str(e)}")
            return service_error_response("WECHAT_ORDER_FAILED", "创建微信支付订单失败")
    
    def _create_stripe_order(self, order: CoinOrder) -> Dict:
        """创建Stripe订单"""
        try:
            import stripe
            
            # 设置Stripe密钥
            stripe.api_key = self.config['stripe']['secret_key']
            
            # 创建Stripe支付意图
            intent = stripe.PaymentIntent.create(
                amount=int(order.amount * 100),  # Stripe金额单位为分
                currency='cny',
                metadata={
                    'order_no': order.order_no,
                    'user_id': order.user_id,
                    'package_id': order.package_id
                }
            )
            
            return service_success_response({
                'client_secret': intent.client_secret,
                'publishable_key': self.config['stripe']['publishable_key'],
                'order_no': order.order_no,
                'amount': order.amount,
                'payment_method': 'STRIPE'
            })
            
        except ImportError:
            # 如果没有安装Stripe SDK，返回模拟数据
            return self._create_mock_payment_order(order, 'STRIPE')
        except Exception as e:
            current_app.logger.error(f"创建Stripe订单失败: {str(e)}")
            return service_error_response("STRIPE_ORDER_FAILED", "创建Stripe订单失败")
    
    def _create_mock_payment_order(self, order: CoinOrder, payment_method: str) -> Dict:
        """创建模拟支付订单（用于开发测试）"""
        mock_data = {
            'ALIPAY': {
                'payment_url': f'https://mock-alipay.com/pay?order_no={order.order_no}&amount={order.amount}',
                'order_no': order.order_no,
                'amount': order.amount,
                'payment_method': 'ALIPAY'
            },
            'WECHAT': {
                'qr_code': f'https://mock-wechat.com/qr?order_no={order.order_no}&amount={order.amount}',
                'order_no': order.order_no,
                'amount': order.amount,
                'payment_method': 'WECHAT'
            },
            'STRIPE': {
                'client_secret': f'mock_client_secret_{order.order_no}',
                'publishable_key': 'pk_test_mock_key',
                'order_no': order.order_no,
                'amount': order.amount,
                'payment_method': 'STRIPE'
            }
        }
        
        return service_success_response(mock_data[payment_method])
    
    def verify_payment(self, payment_method: str, payment_data: Dict) -> Dict:
        """验证支付结果"""
        try:
            if payment_method == 'ALIPAY':
                return self._verify_alipay_payment(payment_data)
            elif payment_method == 'WECHAT':
                return self._verify_wechat_payment(payment_data)
            elif payment_method == 'STRIPE':
                return self._verify_stripe_payment(payment_data)
            else:
                return service_error_response("UNSUPPORTED_PAYMENT_METHOD", "不支持的支付方式")
                
        except Exception as e:
            current_app.logger.error(f"验证支付失败: {str(e)}")
            return service_error_response("VERIFY_PAYMENT_FAILED", "验证支付失败")
    
    def _verify_alipay_payment(self, payment_data: Dict) -> Dict:
        """验证支付宝支付"""
        # 这里应该实现支付宝支付验证逻辑
        # 包括签名验证、订单状态检查等
        return service_success_response({'verified': True, 'order_no': payment_data.get('out_trade_no')})
    
    def _verify_wechat_payment(self, payment_data: Dict) -> Dict:
        """验证微信支付"""
        # 这里应该实现微信支付验证逻辑
        return service_success_response({'verified': True, 'order_no': payment_data.get('out_trade_no')})
    
    def _verify_stripe_payment(self, payment_data: Dict) -> Dict:
        """验证Stripe支付"""
        # 这里应该实现Stripe支付验证逻辑
        return service_success_response({'verified': True, 'payment_intent_id': payment_data.get('payment_intent_id')})
    
    def _generate_nonce_str(self) -> str:
        """生成随机字符串"""
        return str(uuid.uuid4()).replace('-', '')
    
    def _generate_wechat_sign(self, params: Dict) -> str:
        """生成微信支付签名"""
        # 排序参数
        sorted_params = sorted(params.items())
        # 拼接字符串
        string_a = '&'.join([f"{k}={v}" for k, v in sorted_params if v])
        # 添加API密钥
        string_sign_temp = f"{string_a}&key={self.config['wechat']['api_key']}"
        # MD5签名
        return hashlib.md5(string_sign_temp.encode('utf-8')).hexdigest().upper()
    
    def _dict_to_xml(self, data: Dict) -> str:
        """字典转XML"""
        xml = '<xml>'
        for k, v in data.items():
            xml += f'<{k}><![CDATA[{v}]]></{k}>'
        xml += '</xml>'
        return xml
    
    def _xml_to_dict(self, xml: str) -> Dict:
        """XML转字典"""
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result


class MockPaymentService(PaymentService):
    """模拟支付服务（用于开发测试）"""
    
    def __init__(self, db_session):
        super().__init__(db_session)
        self.mock_payments = {}  # 存储模拟支付数据
    
    def create_payment_order(self, order_id: int, payment_method: str) -> Dict:
        """创建模拟支付订单"""
        try:
            order = self.db.query(CoinOrder).filter(CoinOrder.id == order_id).first()
            if not order:
                return service_error_response("ORDER_NOT_FOUND", "订单不存在")
            
            # 生成模拟支付ID
            mock_payment_id = f"mock_{payment_method.lower()}_{int(time.time())}"
            
            # 存储模拟支付数据
            self.mock_payments[mock_payment_id] = {
                'order_id': order_id,
                'order_no': order.order_no,
                'amount': order.amount,
                'payment_method': payment_method,
                'status': 'PENDING',
                'created_at': datetime.utcnow()
            }
            
            # 返回支付信息
            if payment_method == 'ALIPAY':
                return service_success_response({
                    'payment_url': f'/mock-payment/alipay/{mock_payment_id}',
                    'order_no': order.order_no,
                    'amount': order.amount,
                    'payment_method': 'ALIPAY',
                    'mock_payment_id': mock_payment_id
                })
            elif payment_method == 'WECHAT':
                return service_success_response({
                    'qr_code': f'/mock-payment/wechat/{mock_payment_id}',
                    'order_no': order.order_no,
                    'amount': order.amount,
                    'payment_method': 'WECHAT',
                    'mock_payment_id': mock_payment_id
                })
            elif payment_method == 'STRIPE':
                return service_success_response({
                    'client_secret': f'mock_client_secret_{mock_payment_id}',
                    'publishable_key': 'pk_test_mock_key',
                    'order_no': order.order_no,
                    'amount': order.amount,
                    'payment_method': 'STRIPE',
                    'mock_payment_id': mock_payment_id
                })
            else:
                return service_error_response("UNSUPPORTED_PAYMENT_METHOD", "不支持的支付方式")
                
        except Exception as e:
            current_app.logger.error(f"创建模拟支付订单失败: {str(e)}")
            return service_error_response("CREATE_MOCK_PAYMENT_FAILED", "创建模拟支付订单失败")
    
    def simulate_payment_success(self, mock_payment_id: str) -> Dict:
        """模拟支付成功"""
        if mock_payment_id not in self.mock_payments:
            return service_error_response("MOCK_PAYMENT_NOT_FOUND", "模拟支付不存在")
        
        payment_data = self.mock_payments[mock_payment_id]
        payment_data['status'] = 'SUCCESS'
        payment_data['paid_at'] = datetime.utcnow()
        
        return service_success_response({
            'verified': True,
            'order_no': payment_data['order_no'],
            'payment_id': mock_payment_id
        })
    
    def simulate_payment_failure(self, mock_payment_id: str) -> Dict:
        """模拟支付失败"""
        if mock_payment_id not in self.mock_payments:
            return service_error_response("MOCK_PAYMENT_NOT_FOUND", "模拟支付不存在")
        
        payment_data = self.mock_payments[mock_payment_id]
        payment_data['status'] = 'FAILED'
        payment_data['failed_at'] = datetime.utcnow()
        
        return service_success_response({
            'verified': False,
            'order_no': payment_data['order_no'],
            'payment_id': mock_payment_id
        })
