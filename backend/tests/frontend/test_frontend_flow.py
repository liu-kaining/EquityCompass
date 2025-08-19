#!/usr/bin/env python3
"""
前端用户流程测试脚本
使用Selenium自动化测试前端界面
"""
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class FrontendFlowTester:
    """前端流程测试器"""
    
    def __init__(self):
        self.base_url = "http://localhost:5001"
        self.driver = None
        self.test_email = "frontend@test.com"
    
    def setup_driver(self):
        """设置Chrome驱动"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Chrome驱动设置成功")
            return True
        except Exception as e:
            print(f"❌ Chrome驱动设置失败: {e}")
            print("💡 请安装Chrome浏览器和ChromeDriver")
            return False
    
    def test_login_page(self):
        """测试登录页面"""
        print("\n🌐 测试登录页面...")
        
        try:
            # 访问登录页面
            self.driver.get(f"{self.base_url}/auth/login")
            
            # 检查页面标题
            assert "智策股析" in self.driver.title
            print("    ✅ 页面标题正确")
            
            # 检查关键元素
            email_input = self.driver.find_element(By.ID, "email")
            send_btn = self.driver.find_element(By.ID, "sendCodeBtn")
            
            assert email_input.is_displayed()
            assert send_btn.is_displayed()
            print("    ✅ 登录表单元素存在")
            
            # 检查开发模式按钮
            dev_toggle = self.driver.find_element(By.CSS_SELECTOR, "[data-bs-target='#devAccounts']")
            dev_toggle.click()
            
            time.sleep(1)
            
            admin_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-email='admin@dev.com']")
            user_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-email='user@dev.com']")
            
            assert admin_btn.is_displayed()
            assert user_btn.is_displayed()
            print("    ✅ 开发模式按钮正常")
            
            print("✅ 登录页面测试通过")
            return True
            
        except Exception as e:
            print(f"    ❌ 登录页面测试失败: {e}")
            return False
    
    def test_dev_login(self):
        """测试开发模式登录"""
        print("\n👨‍💻 测试开发模式登录...")
        
        try:
            # 点击普通用户按钮
            user_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-email='user@dev.com']")
            user_btn.click()
            
            # 等待跳转到仪表板
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/dashboard")
            )
            
            # 检查是否成功登录
            assert "/dashboard" in self.driver.current_url
            print("    ✅ 成功跳转到仪表板")
            
            # 检查页面内容
            assert "仪表板" in self.driver.page_source or "dashboard" in self.driver.page_source.lower()
            print("    ✅ 仪表板页面加载正常")
            
            print("✅ 开发模式登录测试通过")
            return True
            
        except Exception as e:
            print(f"    ❌ 开发模式登录测试失败: {e}")
            return False
    
    def test_normal_login_flow(self):
        """测试正常登录流程"""
        print("\n📧 测试正常登录流程...")
        
        try:
            # 返回登录页面
            self.driver.get(f"{self.base_url}/auth/login")
            
            # 输入邮箱
            email_input = self.driver.find_element(By.ID, "email")
            email_input.clear()
            email_input.send_keys(self.test_email)
            
            # 点击发送验证码
            send_btn = self.driver.find_element(By.ID, "sendCodeBtn")
            send_btn.click()
            
            # 等待跳转到验证页面
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/auth/verify")
            )
            
            assert "/auth/verify" in self.driver.current_url
            print("    ✅ 成功跳转到验证页面")
            
            # 检查验证页面元素
            code_input = self.driver.find_element(By.ID, "code")
            verify_btn = self.driver.find_element(By.ID, "verifyBtn")
            
            assert code_input.is_displayed()
            assert verify_btn.is_displayed()
            print("    ✅ 验证页面元素正常")
            
            # 检查邮箱显示
            assert self.test_email in self.driver.page_source
            print("    ✅ 邮箱地址显示正确")
            
            print("✅ 正常登录流程测试通过")
            return True
            
        except Exception as e:
            print(f"    ❌ 正常登录流程测试失败: {e}")
            return False
    
    def test_verification_page(self):
        """测试验证码页面功能"""
        print("\n🔐 测试验证码页面功能...")
        
        try:
            # 输入无效验证码
            code_input = self.driver.find_element(By.ID, "code")
            code_input.clear()
            code_input.send_keys("123")
            
            verify_btn = self.driver.find_element(By.ID, "verifyBtn")
            verify_btn.click()
            
            time.sleep(1)
            
            # 检查错误提示
            error_feedback = self.driver.find_element(By.CLASS_NAME, "invalid-feedback")
            assert "6位" in error_feedback.text
            print("    ✅ 验证码长度验证正常")
            
            # 输入非数字验证码
            code_input.clear()
            code_input.send_keys("abcdef")
            
            # JavaScript应该阻止非数字输入
            actual_value = code_input.get_attribute("value")
            assert not any(c.isalpha() for c in actual_value)
            print("    ✅ 非数字输入过滤正常")
            
            # 测试重新发送按钮
            resend_btn = self.driver.find_element(By.ID, "resendBtn")
            assert resend_btn.is_displayed()
            print("    ✅ 重新发送按钮存在")
            
            print("✅ 验证码页面功能测试通过")
            return True
            
        except Exception as e:
            print(f"    ❌ 验证码页面功能测试失败: {e}")
            return False
    
    def test_responsive_design(self):
        """测试响应式设计"""
        print("\n📱 测试响应式设计...")
        
        try:
            # 测试移动端尺寸
            self.driver.set_window_size(375, 667)  # iPhone 6/7/8
            time.sleep(1)
            
            # 返回登录页面
            self.driver.get(f"{self.base_url}/auth/login")
            
            # 检查元素是否仍然可见
            email_input = self.driver.find_element(By.ID, "email")
            send_btn = self.driver.find_element(By.ID, "sendCodeBtn")
            
            assert email_input.is_displayed()
            assert send_btn.is_displayed()
            print("    ✅ 移动端布局正常")
            
            # 恢复桌面尺寸
            self.driver.set_window_size(1920, 1080)
            print("    ✅ 响应式设计测试通过")
            
            print("✅ 响应式设计测试通过")
            return True
            
        except Exception as e:
            print(f"    ❌ 响应式设计测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始前端用户流程测试...")
        
        # 首先检查应用是否运行
        try:
            response = requests.get(f"{self.base_url}/auth/login", timeout=5)
            if response.status_code != 200:
                print(f"❌ 应用未运行或不可访问 (状态码: {response.status_code})")
                return
        except Exception as e:
            print(f"❌ 无法连接到应用: {e}")
            print("💡 请确保Flask应用在 http://localhost:5001 运行")
            return
        
        # 设置浏览器驱动
        if not self.setup_driver():
            print("❌ 无法设置浏览器驱动，跳过前端测试")
            print("💡 如需完整测试，请安装Chrome和ChromeDriver")
            return
        
        try:
            results = []
            
            # 运行各项测试
            results.append(self.test_login_page())
            results.append(self.test_dev_login())
            results.append(self.test_normal_login_flow())
            results.append(self.test_verification_page())
            results.append(self.test_responsive_design())
            
            # 统计结果
            passed = sum(results)
            total = len(results)
            
            print("\n" + "="*60)
            print("📋 前端测试总结")
            print("="*60)
            print(f"✅ 通过: {passed}")
            print(f"❌ 失败: {total - passed}")
            print(f"📊 总计: {total}")
            
            success_rate = (passed / total) * 100
            print(f"📈 成功率: {success_rate:.1f}%")
            
            if passed == total:
                print("\n🎉 恭喜！前端所有测试通过，界面功能正常！")
            else:
                print(f"\n⚠️ 前端存在 {total - passed} 个问题，建议检查修复")
                
        except Exception as e:
            print(f"❌ 测试过程中出错: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🧹 浏览器驱动已关闭")


def simple_http_test():
    """简单的HTTP测试（不需要Selenium）"""
    print("🌐 执行简单HTTP测试...")
    base_url = "http://localhost:5001"
    
    try:
        # 测试登录页面
        response = requests.get(f"{base_url}/auth/login")
        print(f"登录页面状态码: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            checks = [
                ("页面标题", "智策股析" in content),
                ("邮箱输入框", 'id="email"' in content),
                ("发送按钮", 'id="sendCodeBtn"' in content),
                ("开发模式", "admin@dev.com" in content),
                ("Font Awesome", "font-awesome" in content or "fas fa-" in content),
                ("Bootstrap", "bootstrap" in content),
            ]
            
            passed = 0
            for name, result in checks:
                if result:
                    print(f"    ✅ {name}")
                    passed += 1
                else:
                    print(f"    ❌ {name}")
            
            print(f"\n✅ HTTP测试通过 {passed}/{len(checks)} 项")
            
            if passed == len(checks):
                print("🎉 前端页面基本功能正常！")
                return True
        else:
            print(f"❌ 登录页面无法访问 (状态码: {response.status_code})")
            
    except Exception as e:
        print(f"❌ HTTP测试失败: {e}")
    
    return False


if __name__ == '__main__':
    # 先执行简单的HTTP测试
    http_success = simple_http_test()
    
    print("\n" + "="*60)
    
    if http_success:
        # 如果HTTP测试通过，可以尝试完整的浏览器测试
        print("HTTP测试通过，尝试完整的浏览器测试...")
        tester = FrontendFlowTester()
        tester.run_all_tests()
    else:
        print("HTTP测试未完全通过，建议先检查基础问题")
