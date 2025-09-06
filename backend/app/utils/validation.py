"""
用户输入验证工具
"""
import re
from typing import Dict, Any


class ValidationError(Exception):
    """验证错误异常"""
    pass


class UserValidator:
    """用户输入验证器"""
    
    # 用户名规则
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 20
    USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'
    USERNAME_RESERVED_WORDS = {
        'admin', 'administrator', 'root', 'user', 'guest', 'test', 'demo',
        'api', 'www', 'mail', 'ftp', 'support', 'help', 'info', 'contact',
        'about', 'home', 'login', 'register', 'signup', 'signin', 'logout',
        'dashboard', 'profile', 'settings', 'account', 'system', 'service',
        'equitycompass', '智策股析', 'stock', 'analysis', 'report'
    }
    
    # 密码规则
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = False  # 暂时不要求特殊字符
    
    # 邮箱规则
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    @classmethod
    def validate_username(cls, username: str) -> Dict[str, Any]:
        """
        验证用户名
        
        Args:
            username: 用户名
            
        Returns:
            验证结果字典
        """
        if not username:
            return {
                'valid': False,
                'error': 'USERNAME_REQUIRED',
                'message': '用户名不能为空'
            }
        
        username = username.strip()
        
        # 长度检查
        if len(username) < cls.USERNAME_MIN_LENGTH:
            return {
                'valid': False,
                'error': 'USERNAME_TOO_SHORT',
                'message': f'用户名至少需要{cls.USERNAME_MIN_LENGTH}个字符'
            }
        
        if len(username) > cls.USERNAME_MAX_LENGTH:
            return {
                'valid': False,
                'error': 'USERNAME_TOO_LONG',
                'message': f'用户名不能超过{cls.USERNAME_MAX_LENGTH}个字符'
            }
        
        # 格式检查
        if not re.match(cls.USERNAME_PATTERN, username):
            return {
                'valid': False,
                'error': 'USERNAME_INVALID_FORMAT',
                'message': '用户名只能包含字母、数字和下划线'
            }
        
        # 保留词检查
        if username.lower() in cls.USERNAME_RESERVED_WORDS:
            return {
                'valid': False,
                'error': 'USERNAME_RESERVED',
                'message': '该用户名已被保留，请选择其他用户名'
            }
        
        # 不能以数字开头
        if username[0].isdigit():
            return {
                'valid': False,
                'error': 'USERNAME_STARTS_WITH_DIGIT',
                'message': '用户名不能以数字开头'
            }
        
        return {
            'valid': True,
            'message': '用户名格式正确'
        }
    
    @classmethod
    def validate_password(cls, password: str) -> Dict[str, Any]:
        """
        验证密码
        
        Args:
            password: 密码
            
        Returns:
            验证结果字典
        """
        if not password:
            return {
                'valid': False,
                'error': 'PASSWORD_REQUIRED',
                'message': '密码不能为空'
            }
        
        # 长度检查
        if len(password) < cls.PASSWORD_MIN_LENGTH:
            return {
                'valid': False,
                'error': 'PASSWORD_TOO_SHORT',
                'message': f'密码至少需要{cls.PASSWORD_MIN_LENGTH}个字符'
            }
        
        if len(password) > cls.PASSWORD_MAX_LENGTH:
            return {
                'valid': False,
                'error': 'PASSWORD_TOO_LONG',
                'message': f'密码不能超过{cls.PASSWORD_MAX_LENGTH}个字符'
            }
        
        # 复杂度检查
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        
        if cls.PASSWORD_REQUIRE_UPPERCASE and not has_upper:
            return {
                'valid': False,
                'error': 'PASSWORD_NO_UPPERCASE',
                'message': '密码必须包含至少一个大写字母'
            }
        
        if cls.PASSWORD_REQUIRE_LOWERCASE and not has_lower:
            return {
                'valid': False,
                'error': 'PASSWORD_NO_LOWERCASE',
                'message': '密码必须包含至少一个小写字母'
            }
        
        if cls.PASSWORD_REQUIRE_DIGIT and not has_digit:
            return {
                'valid': False,
                'error': 'PASSWORD_NO_DIGIT',
                'message': '密码必须包含至少一个数字'
            }
        
        return {
            'valid': True,
            'message': '密码格式正确'
        }
    
    @classmethod
    def validate_email(cls, email: str) -> Dict[str, Any]:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            验证结果字典
        """
        if not email:
            return {
                'valid': False,
                'error': 'EMAIL_REQUIRED',
                'message': '邮箱地址不能为空'
            }
        
        email = email.strip().lower()
        
        if not re.match(cls.EMAIL_PATTERN, email):
            return {
                'valid': False,
                'error': 'EMAIL_INVALID_FORMAT',
                'message': '邮箱格式不正确'
            }
        
        return {
            'valid': True,
            'message': '邮箱格式正确'
        }
    
    @classmethod
    def validate_registration_data(cls, username: str, email: str, password: str, confirm_password: str = None) -> Dict[str, Any]:
        """
        验证注册数据
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            confirm_password: 确认密码
            
        Returns:
            验证结果字典
        """
        # 验证用户名
        username_result = cls.validate_username(username)
        if not username_result['valid']:
            return username_result
        
        # 验证邮箱
        email_result = cls.validate_email(email)
        if not email_result['valid']:
            return email_result
        
        # 验证密码
        password_result = cls.validate_password(password)
        if not password_result['valid']:
            return password_result
        
        # 验证确认密码
        if confirm_password is not None and password != confirm_password:
            return {
                'valid': False,
                'error': 'PASSWORD_MISMATCH',
                'message': '两次输入的密码不一致'
            }
        
        return {
            'valid': True,
            'message': '注册信息验证通过'
        }


def is_valid_username(username: str) -> bool:
    """快速检查用户名是否有效"""
    return UserValidator.validate_username(username)['valid']


def is_valid_password(password: str) -> bool:
    """快速检查密码是否有效"""
    return UserValidator.validate_password(password)['valid']


def is_valid_email(email: str) -> bool:
    """快速检查邮箱是否有效"""
    return UserValidator.validate_email(email)['valid']
