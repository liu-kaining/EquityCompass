#!/usr/bin/env python3
"""
简单的前端测试脚本
不需要Selenium，只使用HTTP请求测试
"""
import requests
import re
from urllib.parse import urljoin


class SimpleFrontendTester:
    """简单前端测试器"""
    
    def __init__(self):
        self.base_url = "http://localhost:5001"
        self.session = requests.Session()
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_login_page(self):
        """测试登录页面"""
        print("🌐 测试登录页面...")
        
        try:
            url = f"{self.base_url}/auth/login"
            response = self.session.get(url)
            
            self._assert(response.status_code == 200, f"登录页面状态码错误: {response.status_code}")
            
            content = response.text
            
            # 检查基本HTML结构
            self._assert("<!DOCTYPE html>" in content or "<html" in content, "缺少HTML文档声明")
            self._assert("智策股析" in content, "页面标题不正确")
            self._assert('<title>' in content, "缺少title标签")
            
            # 检查关键表单元素
            self._assert('id="email"' in content, "缺少邮箱输入框")
            self._assert('type="email"' in content, "邮箱输入框类型不正确")
            self._assert('id="sendCodeBtn"' in content, "缺少发送验证码按钮")
            self._assert('method="POST"' in content, "表单方法不正确")
            
            # 检查开发模式功能
            self._assert('admin@dev.com' in content, "缺少管理员测试账号")
            self._assert('user@dev.com' in content, "缺少普通用户测试账号")
            
            # 检查CSS和JS资源
            self._assert('bootstrap' in content.lower(), "缺少Bootstrap CSS")
            self._assert('font-awesome' in content.lower() or 'fas fa-' in content, "缺少Font Awesome图标")
            
            # 检查JavaScript功能
            self._assert('addEventListener' in content, "缺少JavaScript事件监听")
            self._assert('fetch(' in content, "缺少AJAX请求代码")
            
            print("    ✅ 登录页面HTML结构正确")
            print("    ✅ 表单元素完整")
            print("    ✅ 开发模式功能存在")
            print("    ✅ CSS/JS资源加载")
            print("✅ 登录页面测试通过")
            
        except Exception as e:
            self._record_error("登录页面测试", e)
    
    def test_verification_page(self):
        """测试验证码页面"""
        print("\n🔐 测试验证码页面...")
        
        try:
            url = f"{self.base_url}/auth/verify?email=test@example.com"
            response = self.session.get(url)
            
            self._assert(response.status_code == 200, f"验证页面状态码错误: {response.status_code}")
            
            content = response.text
            
            # 检查基本结构
            self._assert("验证码" in content, "页面标题不正确")
            self._assert("test@example.com" in content, "邮箱地址未显示")
            
            # 检查表单元素
            self._assert('id="code"' in content, "缺少验证码输入框")
            self._assert('maxlength="6"' in content, "验证码输入框长度限制不正确")
            self._assert('id="verifyBtn"' in content, "缺少验证按钮")
            
            # 检查重新发送功能
            self._assert('id="resendBtn"' in content, "缺少重新发送按钮")
            self._assert('countdown' in content.lower(), "缺少倒计时功能")
            
            # 检查返回登录链接
            self._assert('/auth/login' in content, "缺少返回登录链接")
            
            print("    ✅ 验证页面HTML结构正确")
            print("    ✅ 表单元素完整")
            print("    ✅ 重新发送功能存在")
            print("    ✅ 导航链接正确")
            print("✅ 验证码页面测试通过")
            
        except Exception as e:
            self._record_error("验证码页面测试", e)
    
    def test_dev_login_flow(self):
        """测试开发模式登录流程"""
        print("\n👨‍💻 测试开发模式登录...")
        
        try:
            # 提交管理员登录
            login_url = f"{self.base_url}/auth/login"
            data = {'email': 'admin@dev.com'}
            
            response = self.session.post(login_url, data=data, allow_redirects=False)
            
            # 应该是302重定向到仪表板
            self._assert(response.status_code == 302, f"登录重定向状态码错误: {response.status_code}")
            
            location = response.headers.get('Location', '')
            self._assert('/dashboard' in location, f"重定向地址错误: {location}")
            
            # 跟随重定向
            dashboard_response = self.session.get(f"{self.base_url}/dashboard")
            self._assert(dashboard_response.status_code == 200, "仪表板页面无法访问")
            
            dashboard_content = dashboard_response.text
            self._assert("仪表板" in dashboard_content or "dashboard" in dashboard_content.lower(), 
                        "仪表板页面内容不正确")
            
            print("    ✅ 管理员登录重定向正确")
            print("    ✅ 仪表板页面可访问")
            print("✅ 开发模式登录测试通过")
            
        except Exception as e:
            self._record_error("开发模式登录测试", e)
    
    def test_ajax_api_integration(self):
        """测试AJAX API集成"""
        print("\n🔗 测试AJAX API集成...")
        
        try:
            # 测试发送验证码API
            api_url = f"{self.base_url}/api/auth/send-code"
            data = {'email': 'ajax@test.com'}
            
            response = self.session.post(api_url, json=data, 
                                       headers={'Content-Type': 'application/json'})
            
            self._assert(response.status_code == 200, f"API状态码错误: {response.status_code}")
            
            json_data = response.json()
            self._assert(json_data.get('success') == True, "API返回success字段不正确")
            self._assert('code' in json_data.get('data', {}), "API未返回验证码（开发模式）")
            
            code = json_data['data']['code']
            print(f"    ✅ 获得验证码: {code}")
            
            # 测试验证API
            verify_url = f"{self.base_url}/api/auth/verify-code"
            verify_data = {'email': 'ajax@test.com', 'code': code}
            
            verify_response = self.session.post(verify_url, json=verify_data,
                                              headers={'Content-Type': 'application/json'})
            
            self._assert(verify_response.status_code == 200, f"验证API状态码错误: {verify_response.status_code}")
            
            verify_json = verify_response.json()
            self._assert(verify_json.get('success') == True, "验证API返回success字段不正确")
            self._assert('access_token' in verify_json.get('data', {}), "验证API未返回访问Token")
            
            print("    ✅ 发送验证码API正常")
            print("    ✅ 验证登录API正常")
            print("    ✅ JWT Token生成正常")
            print("✅ AJAX API集成测试通过")
            
        except Exception as e:
            self._record_error("AJAX API集成测试", e)
    
    def test_static_resources(self):
        """测试静态资源"""
        print("\n📁 测试静态资源...")
        
        try:
            # 测试CSS文件
            css_url = f"{self.base_url}/static/css/style.css"
            css_response = self.session.get(css_url)
            
            # CSS文件可能不存在，这是正常的（使用内联样式）
            if css_response.status_code == 200:
                print("    ✅ 自定义CSS文件存在")
            else:
                print("    ℹ️ 自定义CSS文件不存在（使用内联样式）")
            
            # 测试JS文件
            js_url = f"{self.base_url}/static/js/main.js"
            js_response = self.session.get(js_url)
            
            if js_response.status_code == 200:
                print("    ✅ 自定义JS文件存在")
            else:
                print("    ℹ️ 自定义JS文件不存在（使用内联脚本）")
            
            # 测试健康检查
            health_url = f"{self.base_url}/api/health"
            health_response = self.session.get(health_url)
            
            if health_response.status_code == 200:
                print("    ✅ 健康检查API正常")
            else:
                print("    ⚠️ 健康检查API不可用")
            
            print("✅ 静态资源测试完成")
            
        except Exception as e:
            self._record_error("静态资源测试", e)
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n❌ 测试错误处理...")
        
        try:
            # 测试无效邮箱
            invalid_email_data = {'email': 'invalid-email'}
            response = self.session.post(f"{self.base_url}/api/auth/send-code", 
                                       json=invalid_email_data,
                                       headers={'Content-Type': 'application/json'})
            
            self._assert(response.status_code == 400, "无效邮箱应返回400状态码")
            
            json_data = response.json()
            self._assert(json_data.get('success') == False, "错误响应success字段应为False")
            self._assert('error' in json_data, "错误响应应包含error字段")
            
            print("    ✅ 无效邮箱错误处理正确")
            
            # 测试错误验证码
            wrong_code_data = {'email': 'test@example.com', 'code': '000000'}
            verify_response = self.session.post(f"{self.base_url}/api/auth/verify-code",
                                              json=wrong_code_data,
                                              headers={'Content-Type': 'application/json'})
            
            self._assert(verify_response.status_code == 400, "错误验证码应返回400状态码")
            
            verify_json = verify_response.json()
            self._assert(verify_json.get('success') == False, "验证错误响应success字段应为False")
            
            print("    ✅ 错误验证码处理正确")
            
            # 测试404页面
            notfound_response = self.session.get(f"{self.base_url}/nonexistent-page")
            self._assert(notfound_response.status_code == 404, "不存在页面应返回404")
            
            print("    ✅ 404错误处理正确")
            print("✅ 错误处理测试通过")
            
        except Exception as e:
            self._record_error("错误处理测试", e)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始前端功能测试...\n")
        
        # 首先检查应用是否可访问
        try:
            response = self.session.get(self.base_url, timeout=5)
            print(f"✅ 应用可访问 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ 无法连接到应用: {e}")
            print("💡 请确保Flask应用在 http://localhost:5001 运行")
            return
        
        # 运行各项测试
        self.test_login_page()
        self.test_verification_page()
        self.test_dev_login_flow()
        self.test_ajax_api_integration()
        self.test_static_resources()
        self.test_error_handling()
        
        # 打印测试总结
        self._print_summary()
    
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
        print("\n" + "="*60)
        print("📋 前端功能测试总结")
        print("="*60)
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"📊 总计: {self.passed + self.failed}")
        
        if self.failed > 0:
            print(f"\n❌ 失败的测试:")
            for error in self.errors:
                print(f"   • {error}")
            print(f"\n🚨 前端存在 {self.failed} 个问题，需要修复！")
        else:
            print(f"\n🎉 恭喜！前端所有测试通过，功能正常！")
        
        success_rate = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        print(f"📈 成功率: {success_rate:.1f}%")


if __name__ == '__main__':
    tester = SimpleFrontendTester()
    tester.run_all_tests()
