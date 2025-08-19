"""
JWT认证服务
负责JWT Token的生成、验证和管理
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from flask import current_app
from functools import wraps


class JWTService:
    """JWT认证服务"""
    
    def __init__(self):
        self.algorithm = 'HS256'
        self.token_expire_hours = 24 * 7  # 7天过期
        self.refresh_token_expire_days = 30  # 刷新Token 30天过期
    
    def _get_secret_key(self) -> str:
        """获取JWT密钥"""
        return current_app.config.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    
    def generate_token(self, user_id: int, email: str, is_admin: bool = False) -> Dict[str, Any]:
        """
        生成JWT Token
        
        Args:
            user_id: 用户ID
            email: 用户邮箱
            is_admin: 是否为管理员
            
        Returns:
            包含access_token和refresh_token的字典
        """
        try:
            now = datetime.utcnow()
            
            # Access Token payload
            access_payload = {
                'user_id': user_id,
                'email': email,
                'is_admin': is_admin,
                'iat': now,
                'exp': now + timedelta(hours=self.token_expire_hours),
                'type': 'access'
            }
            
            # Refresh Token payload
            refresh_payload = {
                'user_id': user_id,
                'email': email,
                'iat': now,
                'exp': now + timedelta(days=self.refresh_token_expire_days),
                'type': 'refresh'
            }
            
            # 生成tokens
            access_token = jwt.encode(
                access_payload, 
                self._get_secret_key(), 
                algorithm=self.algorithm
            )
            
            refresh_token = jwt.encode(
                refresh_payload, 
                self._get_secret_key(), 
                algorithm=self.algorithm
            )
            
            return {
                'success': True,
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': self.token_expire_hours * 3600,
                    'user': {
                        'id': user_id,
                        'email': email,
                        'is_admin': is_admin
                    }
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"生成JWT Token失败: {e}")
            return {
                'success': False,
                'error': 'TOKEN_GENERATION_FAILED',
                'message': 'Token生成失败'
            }
    
    def verify_token(self, token: str, token_type: str = 'access') -> Dict[str, Any]:
        """
        验证JWT Token
        
        Args:
            token: JWT Token字符串
            token_type: Token类型 ('access' 或 'refresh')
            
        Returns:
            验证结果和用户信息
        """
        try:
            # 解码token
            payload = jwt.decode(
                token, 
                self._get_secret_key(), 
                algorithms=[self.algorithm]
            )
            
            # 检查token类型
            if payload.get('type') != token_type:
                return {
                    'success': False,
                    'error': 'INVALID_TOKEN_TYPE',
                    'message': f'无效的Token类型，期望: {token_type}'
                }
            
            # 检查是否过期
            exp = payload.get('exp')
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                return {
                    'success': False,
                    'error': 'TOKEN_EXPIRED',
                    'message': 'Token已过期'
                }
            
            return {
                'success': True,
                'data': {
                    'user_id': payload.get('user_id'),
                    'email': payload.get('email'),
                    'is_admin': payload.get('is_admin', False),
                    'exp': exp
                }
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'TOKEN_EXPIRED',
                'message': 'Token已过期'
            }
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"无效的JWT Token: {e}")
            return {
                'success': False,
                'error': 'INVALID_TOKEN',
                'message': '无效的Token'
            }
        except Exception as e:
            current_app.logger.error(f"验证JWT Token失败: {e}")
            return {
                'success': False,
                'error': 'TOKEN_VERIFICATION_FAILED',
                'message': 'Token验证失败'
            }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新访问Token
        
        Args:
            refresh_token: 刷新Token
            
        Returns:
            新的访问Token
        """
        # 验证刷新Token
        result = self.verify_token(refresh_token, 'refresh')
        if not result['success']:
            return result
        
        user_data = result['data']
        
        # 生成新的访问Token
        return self.generate_token(
            user_data['user_id'],
            user_data['email'],
            user_data['is_admin']
        )
    
    def revoke_token(self, token: str) -> Dict[str, Any]:
        """
        撤销Token（将Token加入黑名单）
        注意：这需要Redis或数据库支持，目前仅返回成功
        
        Args:
            token: 要撤销的Token
            
        Returns:
            撤销结果
        """
        try:
            # TODO: 将token加入黑名单（需要Redis支持）
            # 这里可以解码token获取exp时间，然后存储到Redis直到过期
            
            return {
                'success': True,
                'message': 'Token已撤销'
            }
        except Exception as e:
            current_app.logger.error(f"撤销Token失败: {e}")
            return {
                'success': False,
                'error': 'TOKEN_REVOKE_FAILED',
                'message': 'Token撤销失败'
            }
    
    def extract_token_from_header(self, authorization_header: str) -> Optional[str]:
        """
        从Authorization头部提取Token
        
        Args:
            authorization_header: Authorization头部值
            
        Returns:
            提取的Token字符串
        """
        if not authorization_header:
            return None
        
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]


# JWT认证装饰器
def jwt_required(f):
    """JWT认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify, g
        
        # 获取Authorization头部
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'MISSING_TOKEN',
                'message': '缺少认证Token'
            }), 401
        
        # 提取Token
        jwt_service = JWTService()
        token = jwt_service.extract_token_from_header(auth_header)
        if not token:
            return jsonify({
                'success': False,
                'error': 'INVALID_TOKEN_FORMAT',
                'message': 'Token格式错误'
            }), 401
        
        # 验证Token
        result = jwt_service.verify_token(token)
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error'],
                'message': result['message']
            }), 401
        
        # 将用户信息存储到g对象中
        g.current_user = result['data']
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @jwt_required
    def decorated_function(*args, **kwargs):
        from flask import jsonify, g
        
        if not g.current_user.get('is_admin', False):
            return jsonify({
                'success': False,
                'error': 'INSUFFICIENT_PRIVILEGES',
                'message': '权限不足，需要管理员权限'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_jwt(f):
    """可选JWT认证装饰器（用户登录时提供额外信息）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, g
        
        # 获取Authorization头部
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # 提取并验证Token
            jwt_service = JWTService()
            token = jwt_service.extract_token_from_header(auth_header)
            if token:
                result = jwt_service.verify_token(token)
                if result['success']:
                    g.current_user = result['data']
        
        # 如果没有Token或验证失败，g.current_user将不存在
        return f(*args, **kwargs)
    
    return decorated_function
