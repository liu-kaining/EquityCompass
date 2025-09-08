"""
认证模块 - 提供用户认证、JWT管理、权限控制等功能
"""

from .jwt_service import JWTService
from .verification_service import VerificationService
from .auth_service import AuthService
from .permissions import (
    login_required,
    admin_required,
    super_admin_required,
    user_management_required,
    statistics_access_required,
    check_report_download_permission,
)

__all__ = [
    "JWTService",
    "VerificationService", 
    "AuthService",
    "login_required",
    "admin_required",
    "super_admin_required",
    "user_management_required",
    "statistics_access_required",
    "check_report_download_permission",
]
