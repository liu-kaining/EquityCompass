"""
JWT 服务 - 提供 JWT Token 的生成、验证和管理功能
"""

import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import wraps


class JWTService:
    """JWT Token 管理服务"""
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """
        初始化 JWT 服务
        
        Args:
            secret_key: JWT 密钥
            algorithm: 加密算法
        """
        self.secret_key = secret_key or "your-secret-key"
        self.algorithm = algorithm
        self.default_expiry = 3600  # 默认1小时过期
    
    def generate_token(self, user_id: int, user_data: Dict[str, Any] = None, 
                      expiry: int = None) -> Dict[str, Any]:
        """
        生成 JWT Token
        
        Args:
            user_id: 用户ID
            user_data: 用户数据
            expiry: 过期时间（秒）
            
        Returns:
            包含 token 和过期时间的字典
        """
        expiry = expiry or self.default_expiry
        now = datetime.utcnow()
        expire_time = now + timedelta(seconds=expiry)
        
        payload = {
            "user_id": user_id,
            "iat": now,
            "exp": expire_time,
            "type": "access"
        }
        
        if user_data:
            payload.update(user_data)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            "token": token,
            "expires_at": expire_time.isoformat(),
            "expires_in": expiry,
            "token_type": "Bearer"
        }
    
    def generate_refresh_token(self, user_id: int, expiry: int = 7 * 24 * 3600) -> str:
        """
        生成刷新 Token
        
        Args:
            user_id: 用户ID
            expiry: 过期时间（秒），默认7天
            
        Returns:
            刷新 Token
        """
        now = datetime.utcnow()
        expire_time = now + timedelta(seconds=expiry)
        
        payload = {
            "user_id": user_id,
            "iat": now,
            "exp": expire_time,
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证 JWT Token
        
        Args:
            token: JWT Token
            
        Returns:
            解析后的 payload 或 None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        刷新 Token
        
        Args:
            refresh_token: 刷新 Token
            
        Returns:
            新的 access token 或 None
        """
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        return self.generate_token(user_id)
    
    def extract_user_id(self, token: str) -> Optional[int]:
        """
        从 Token 中提取用户ID
        
        Args:
            token: JWT Token
            
        Returns:
            用户ID 或 None
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        检查 Token 是否过期
        
        Args:
            token: JWT Token
            
        Returns:
            True 如果过期，False 如果未过期
        """
        payload = self.verify_token(token)
        if not payload:
            return True
        
        exp = payload.get("exp")
        if not exp:
            return True
        
        return time.time() > exp


def jwt_required(f):
    """
    JWT 认证装饰器
    
    Usage:
        @jwt_required
        def protected_route():
            return "Protected content"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify
        
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token format error'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        jwt_service = JWTService()
        payload = jwt_service.verify_token(token)
        
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # 将用户信息添加到请求上下文
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """
    获取当前用户信息
    
    Returns:
        当前用户信息字典
    """
    from flask import request
    return getattr(request, 'current_user', None)
