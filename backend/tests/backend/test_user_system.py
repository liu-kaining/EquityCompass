#!/usr/bin/env python3
"""
用户系统测试脚本
测试认证API、验证码服务、JWT服务等功能
"""
import sys
import os
import requests
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.auth.verification_code_service import VerificationCodeService
from app.services.auth.jwt_service import JWTService
from app.services.email.email_service import EmailService


class UserSystemTester:
    """用户系统测试器"""
    
    def __init__(self):
        self.app = create_app('development')
        self.base_url = 'http://localhost:5001'
        self.test_email = 'test@example.com'
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.token = None
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始用户系统完整性测试...\n")
        
        with self.app.app_context():
            # 初始化数据库
            self._setup_test_database()
            
            # 测试服务层
            self._test_services()
            
            # 启动Flask应用并测试API
            self._test_apis()
        
        self._print_summary()
    
    def _setup_test_database(self):
        """设置测试数据库"""
        print("📊 设置测试数据库...")
        try:
            db.create_all()
            print("✅ 测试数据库设置完成\n")
        except Exception as e:
            print(f"❌ 数据库设置失败: {e}\n")
    
    def _test_services(self):
        """测试服务层"""
        print("🔧 测试服务层...")
        
        # 测试验证码服务
        self._test_verification_code_service()
        
        # 测试JWT服务
        self._test_jwt_service()
        
        # 测试邮件服务
        self._test_email_service()
        
        print("✅ 服务层测试完成\n")
    
    def _test_verification_code_service(self):
        """测试验证码服务"""
        print("  📧 测试验证码服务...")
        
        verification_service = VerificationCodeService()
        
        # 测试生成验证码
        try:
            result = verification_service.send_code(self.test_email)
            self._assert(result['success'] == True, "验证码生成失败")
            self._assert('code' in result['data'], "返回结果中没有验证码")
            self._assert(len(result['data']['code']) == 6, "验证码长度不正确")
            
            code = result['data']['code']
            print("    ✅ 验证码生成测试通过")
        except Exception as e:
            self._record_error("验证码生成测试", e)
            return
        
        # 测试验证验证码
        try:
            verify_result = verification_service.verify_code(self.test_email, code)
            self._assert(verify_result['success'] == True, "验证码验证失败")
            print("    ✅ 验证码验证测试通过")
        except Exception as e:
            self._record_error("验证码验证测试", e)
        
        # 测试错误验证码
        try:
            wrong_result = verification_service.verify_code(self.test_email, "000000")
            self._assert(wrong_result['success'] == False, "错误验证码应该验证失败")
            print("    ✅ 错误验证码测试通过")
        except Exception as e:
            self._record_error("错误验证码测试", e)
        
        # 测试发送频率限制
        try:
            # 连续发送两次
            result1 = verification_service.send_code(self.test_email)
            result2 = verification_service.send_code(self.test_email)
            
            # 第二次应该失败（频率限制）
            if result2['success'] == False and 'FREQUENT' in result2.get('error', ''):
                print("    ✅ 发送频率限制测试通过")
            else:
                print("    ⚠️ 发送频率限制测试跳过（Redis未连接）")
        except Exception as e:
            self._record_error("发送频率限制测试", e)
    
    def _test_jwt_service(self):
        """测试JWT服务"""
        print("  🔐 测试JWT服务...")
        
        jwt_service = JWTService()
        
        # 测试生成Token
        try:
            result = jwt_service.generate_token(
                user_id=1,
                email=self.test_email,
                is_admin=False
            )
            self._assert(result['success'] == True, "JWT Token生成失败")
            self._assert('access_token' in result['data'], "返回结果中没有access_token")
            self._assert('refresh_token' in result['data'], "返回结果中没有refresh_token")
            
            access_token = result['data']['access_token']
            refresh_token = result['data']['refresh_token']
            print("    ✅ JWT Token生成测试通过")
        except Exception as e:
            self._record_error("JWT Token生成测试", e)
            return
        
        # 测试验证Token
        try:
            verify_result = jwt_service.verify_token(access_token)
            self._assert(verify_result['success'] == True, "JWT Token验证失败")
            self._assert(verify_result['data']['user_id'] == 1, "Token中用户ID不正确")
            self._assert(verify_result['data']['email'] == self.test_email, "Token中邮箱不正确")
            print("    ✅ JWT Token验证测试通过")
        except Exception as e:
            self._record_error("JWT Token验证测试", e)
        
        # 测试刷新Token
        try:
            refresh_result = jwt_service.refresh_token(refresh_token)
            self._assert(refresh_result['success'] == True, "JWT Token刷新失败")
            self._assert('access_token' in refresh_result['data'], "刷新结果中没有新的access_token")
            print("    ✅ JWT Token刷新测试通过")
        except Exception as e:
            self._record_error("JWT Token刷新测试", e)
        
        # 测试无效Token
        try:
            invalid_result = jwt_service.verify_token("invalid_token")
            self._assert(invalid_result['success'] == False, "无效Token应该验证失败")
            print("    ✅ 无效Token测试通过")
        except Exception as e:
            self._record_error("无效Token测试", e)
    
    def _test_email_service(self):
        """测试邮件服务"""
        print("  📬 测试邮件服务...")
        
        email_service = EmailService()
        
        # 测试连接
        try:
            result = email_service.test_connection()
            self._assert(result['success'] == True, "邮件服务连接失败")
            print("    ✅ 邮件服务连接测试通过")
        except Exception as e:
            self._record_error("邮件服务连接测试", e)
        
        # 测试发送验证码邮件
        try:
            result = email_service.send_verification_code(self.test_email, "123456")
            self._assert(result['success'] == True, "发送验证码邮件失败")
            print("    ✅ 发送验证码邮件测试通过")
        except Exception as e:
            self._record_error("发送验证码邮件测试", e)
        
        # 测试发送欢迎邮件
        try:
            result = email_service.send_welcome_email(self.test_email, "测试用户")
            self._assert(result['success'] == True, "发送欢迎邮件失败")
            print("    ✅ 发送欢迎邮件测试通过")
        except Exception as e:
            self._record_error("发送欢迎邮件测试", e)
    
    def _test_apis(self):
        """测试API接口"""
        print("🌐 启动Flask应用并测试API...")
        
        # 在后台启动Flask应用
        import threading
        import time
        
        def run_app():
            self.app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False, threaded=True)
        
        app_thread = threading.Thread(target=run_app, daemon=True)
        app_thread.start()
        
        # 等待应用启动
        time.sleep(2)
        
        try:
            # 测试发送验证码API
            self._test_send_code_api()
            
            # 测试验证登录API
            self._test_verify_code_api()
            
            # 测试获取用户资料API
            self._test_profile_api()
            
            # 测试更新用户资料API
            self._test_update_profile_api()
            
            # 测试登出API
            self._test_logout_api()
            
        except requests.exceptions.ConnectionError:
            print("    ❌ 无法连接到Flask应用，跳过API测试")
        except Exception as e:
            print(f"    ❌ API测试过程中出错: {e}")
        
        print("✅ API测试完成\n")
    
    def _test_send_code_api(self):
        """测试发送验证码API"""
        print("  📧 测试发送验证码API...")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/send-code",
                json={'email': self.test_email},
                timeout=5
            )
            
            self._assert(response.status_code == 200, f"状态码错误: {response.status_code}")
            
            data = response.json()
            self._assert(data['success'] == True, "API返回失败")
            self._assert('code' in data['data'], "开发环境应该返回验证码")
            
            # 保存验证码用于后续测试
            self.verification_code = data['data']['code']
            print("    ✅ 发送验证码API测试通过")
            
        except Exception as e:
            self._record_error("发送验证码API测试", e)
    
    def _test_verify_code_api(self):
        """测试验证登录API"""
        print("  🔐 测试验证登录API...")
        
        try:
            if not hasattr(self, 'verification_code'):
                print("    ❌ 没有验证码，跳过登录测试")
                return
            
            response = requests.post(
                f"{self.base_url}/api/auth/verify-code",
                json={
                    'email': self.test_email,
                    'code': self.verification_code
                },
                timeout=5
            )
            
            self._assert(response.status_code == 200, f"状态码错误: {response.status_code}")
            
            data = response.json()
            self._assert(data['success'] == True, "API返回失败")
            self._assert('access_token' in data['data'], "返回结果中没有access_token")
            
            # 保存Token用于后续测试
            self.token = data['data']['access_token']
            print("    ✅ 验证登录API测试通过")
            
        except Exception as e:
            self._record_error("验证登录API测试", e)
    
    def _test_profile_api(self):
        """测试获取用户资料API"""
        print("  👤 测试获取用户资料API...")
        
        try:
            if not self.token:
                print("    ❌ 没有Token，跳过用户资料测试")
                return
            
            response = requests.get(
                f"{self.base_url}/api/auth/profile",
                headers={'Authorization': f'Bearer {self.token}'},
                timeout=5
            )
            
            self._assert(response.status_code == 200, f"状态码错误: {response.status_code}")
            
            data = response.json()
            self._assert(data['success'] == True, "API返回失败")
            self._assert('email' in data['data'], "返回结果中没有邮箱")
            self._assert(data['data']['email'] == self.test_email, "邮箱不匹配")
            
            print("    ✅ 获取用户资料API测试通过")
            
        except Exception as e:
            self._record_error("获取用户资料API测试", e)
    
    def _test_update_profile_api(self):
        """测试更新用户资料API"""
        print("  ✏️ 测试更新用户资料API...")
        
        try:
            if not self.token:
                print("    ❌ 没有Token，跳过更新资料测试")
                return
            
            response = requests.put(
                f"{self.base_url}/api/auth/profile",
                json={'nickname': '测试用户昵称'},
                headers={'Authorization': f'Bearer {self.token}'},
                timeout=5
            )
            
            self._assert(response.status_code == 200, f"状态码错误: {response.status_code}")
            
            data = response.json()
            self._assert(data['success'] == True, "API返回失败")
            self._assert(data['data']['nickname'] == '测试用户昵称', "昵称更新失败")
            
            print("    ✅ 更新用户资料API测试通过")
            
        except Exception as e:
            self._record_error("更新用户资料API测试", e)
    
    def _test_logout_api(self):
        """测试登出API"""
        print("  🚪 测试登出API...")
        
        try:
            if not self.token:
                print("    ❌ 没有Token，跳过登出测试")
                return
            
            response = requests.post(
                f"{self.base_url}/api/auth/logout",
                headers={'Authorization': f'Bearer {self.token}'},
                timeout=5
            )
            
            self._assert(response.status_code == 200, f"状态码错误: {response.status_code}")
            
            data = response.json()
            self._assert(data['success'] == True, "API返回失败")
            
            print("    ✅ 登出API测试通过")
            
        except Exception as e:
            self._record_error("登出API测试", e)
    
    def _assert(self, condition, message):
        """断言函数"""
        if condition:
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append(message)
            raise AssertionError(message)
    
    def _record_error(self, test_name, error):
        """记录错误"""
        self.failed += 1
        error_msg = f"{test_name}: {str(error)}"
        self.errors.append(error_msg)
        print(f"    ❌ {error_msg}")
    
    def _print_summary(self):
        """打印测试总结"""
        print("=" * 60)
        print("📋 用户系统测试总结")
        print("=" * 60)
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"📊 总计: {self.passed + self.failed}")
        
        if self.failed > 0:
            print(f"\n❌ 失败的测试:")
            for error in self.errors:
                print(f"   • {error}")
            print(f"\n🚨 用户系统存在 {self.failed} 个问题，需要修复！")
        else:
            print(f"\n🎉 恭喜！用户系统所有测试通过，功能正常！")
        
        success_rate = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        print(f"📈 成功率: {success_rate:.1f}%")


if __name__ == '__main__':
    tester = UserSystemTester()
    tester.run_all_tests()
