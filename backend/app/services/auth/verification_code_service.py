"""
验证码服务
负责生成、存储、验证邮箱验证码
"""
import random
import redis
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import current_app


class VerificationCodeService:
    """验证码服务"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client or self._get_redis_client()
        self.code_length = 6
        self.expire_minutes = 10
        self.rate_limit_seconds = 60  # 1分钟内最多发送1次
    
    def _get_redis_client(self) -> redis.Redis:
        """获取Redis客户端"""
        try:
            client = redis.Redis(
                host=current_app.config.get('REDIS_HOST', 'localhost'),
                port=current_app.config.get('REDIS_PORT', 6379),
                db=current_app.config.get('REDIS_DB', 0),
                decode_responses=True,
                socket_connect_timeout=1,  # 1秒连接超时
                socket_timeout=1
            )
            # 测试连接
            client.ping()
            return client
        except Exception as e:
            current_app.logger.warning(f"Redis连接失败，使用内存存储: {e}")
            # 开发环境可以使用内存存储
            return None
    
    def generate_code(self) -> str:
        """生成6位数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(self.code_length)])
    
    def send_code(self, email: str) -> Dict[str, Any]:
        """
        为邮箱生成并存储验证码
        
        Args:
            email: 邮箱地址
            
        Returns:
            Dict包含操作结果和信息
        """
        try:
            # 检查发送频率限制
            if not self._check_rate_limit(email):
                return {
                    'success': False,
                    'error': 'SEND_TOO_FREQUENT',
                    'message': '验证码发送过于频繁，请稍后再试'
                }
            
            # 生成验证码
            code = self.generate_code()
            
            # 存储验证码
            success = self._store_code(email, code)
            if not success:
                return {
                    'success': False,
                    'error': 'STORAGE_FAILED',
                    'message': '验证码存储失败'
                }
            
            # 设置发送频率限制
            self._set_rate_limit(email)
            
            return {
                'success': True,
                'data': {
                    'code': code,  # 开发环境返回验证码，生产环境需要移除
                    'expires_in': self.expire_minutes * 60,
                    'email': email
                },
                'message': '验证码已生成'
            }
            
        except Exception as e:
            current_app.logger.error(f"生成验证码失败: {e}")
            return {
                'success': False,
                'error': 'GENERATION_FAILED',
                'message': '验证码生成失败'
            }
    
    def verify_code(self, email: str, code: str) -> Dict[str, Any]:
        """
        验证邮箱验证码
        
        Args:
            email: 邮箱地址
            code: 验证码
            
        Returns:
            Dict包含验证结果
        """
        try:
            # 获取存储的验证码
            stored_data = self._get_stored_code(email)
            if not stored_data:
                return {
                    'success': False,
                    'error': 'CODE_NOT_FOUND',
                    'message': '验证码不存在或已过期'
                }
            
            stored_code = stored_data.get('code')
            created_at = stored_data.get('created_at')
            
            # 检查是否过期
            if self._is_expired(created_at):
                self._delete_code(email)  # 清理过期验证码
                return {
                    'success': False,
                    'error': 'CODE_EXPIRED',
                    'message': '验证码已过期'
                }
            
            # 验证码比较
            if stored_code != code:
                return {
                    'success': False,
                    'error': 'CODE_INVALID',
                    'message': '验证码错误'
                }
            
            # 验证成功，清理验证码
            self._delete_code(email)
            
            return {
                'success': True,
                'message': '验证码验证成功'
            }
            
        except Exception as e:
            current_app.logger.error(f"验证码验证失败: {e}")
            return {
                'success': False,
                'error': 'VERIFICATION_FAILED',
                'message': '验证码验证失败'
            }
    
    def _check_rate_limit(self, email: str) -> bool:
        """检查发送频率限制"""
        if not self.redis:
            return True  # 无Redis时跳过限制检查
        
        key = f"rate_limit:{email}"
        return not self.redis.exists(key)
    
    def _set_rate_limit(self, email: str):
        """设置发送频率限制"""
        if not self.redis:
            return
        
        key = f"rate_limit:{email}"
        self.redis.setex(key, self.rate_limit_seconds, "1")
    
    def _store_code(self, email: str, code: str) -> bool:
        """存储验证码"""
        try:
            data = {
                'code': code,
                'created_at': datetime.utcnow().isoformat(),
                'email': email
            }
            
            if self.redis:
                # 使用Redis存储
                key = f"verification_code:{email}"
                self.redis.setex(
                    key, 
                    self.expire_minutes * 60, 
                    str(data)  # Redis存储为字符串
                )
            else:
                # 开发环境使用内存存储（仅用于测试）
                if not hasattr(current_app, '_verification_codes'):
                    current_app._verification_codes = {}
                current_app._verification_codes[email] = data
            
            return True
        except Exception as e:
            current_app.logger.error(f"存储验证码失败: {e}")
            return False
    
    def _get_stored_code(self, email: str) -> Optional[Dict[str, Any]]:
        """获取存储的验证码"""
        try:
            if self.redis:
                # 从Redis获取
                key = f"verification_code:{email}"
                data_str = self.redis.get(key)
                if data_str:
                    # 简单的字符串解析（生产环境建议使用JSON）
                    import ast
                    return ast.literal_eval(data_str)
            else:
                # 从内存获取
                if hasattr(current_app, '_verification_codes'):
                    return current_app._verification_codes.get(email)
            
            return None
        except Exception as e:
            current_app.logger.error(f"获取验证码失败: {e}")
            return None
    
    def _delete_code(self, email: str):
        """删除验证码"""
        try:
            if self.redis:
                key = f"verification_code:{email}"
                self.redis.delete(key)
            else:
                if hasattr(current_app, '_verification_codes'):
                    current_app._verification_codes.pop(email, None)
        except Exception as e:
            current_app.logger.error(f"删除验证码失败: {e}")
    
    def _is_expired(self, created_at_str: str) -> bool:
        """检查验证码是否过期"""
        try:
            created_at = datetime.fromisoformat(created_at_str)
            expire_time = created_at + timedelta(minutes=self.expire_minutes)
            return datetime.utcnow() > expire_time
        except Exception:
            return True  # 解析失败视为过期
    
    def cleanup_expired_codes(self):
        """清理过期的验证码（定期任务调用）"""
        try:
            if not self.redis:
                # 内存存储的清理
                if hasattr(current_app, '_verification_codes'):
                    expired_emails = []
                    for email, data in current_app._verification_codes.items():
                        if self._is_expired(data.get('created_at', '')):
                            expired_emails.append(email)
                    
                    for email in expired_emails:
                        current_app._verification_codes.pop(email, None)
                    
                    current_app.logger.info(f"清理了 {len(expired_emails)} 个过期验证码")
        except Exception as e:
            current_app.logger.error(f"清理过期验证码失败: {e}")
