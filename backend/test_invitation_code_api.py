#!/usr/bin/env python3
"""
邀请码系统API测试脚本
测试所有邀请码相关的API端点
"""
import sys
import os
import requests
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = 'http://localhost:5002'

def print_section(title):
    """打印测试章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_test(test_name):
    """打印测试名称"""
    print(f"\n📋 测试: {test_name}")

def print_success(message):
    """打印成功消息"""
    print(f"✅ {message}")

def print_error(message):
    """打印错误消息"""
    print(f"❌ {message}")

def print_warning(message):
    """打印警告消息"""
    print(f"⚠️  {message}")

def print_info(message):
    """打印信息消息"""
    print(f"ℹ️  {message}")

class APITester:
    """API测试类"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        self.admin_session_id = None
        
    def login_as_admin(self):
        """以管理员身份登录"""
        print_test("管理员登录")
        
        login_data = {
            'username': 'admin',
            'password': 'admin123456'
        }
        
        try:
            # 使用Session登录（设置cookie）
            response = self.session.post(
                f'{self.base_url}/api/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print_success(f"登录成功: {data['data']['user']['username']}")
                    return True
                else:
                    print_error(f"登录失败: {data.get('message')}")
                    return False
            else:
                print_error(f"登录失败，状态码: {response.status_code}")
                print(response.text)
                return False
                
        except requests.exceptions.ConnectionError:
            print_error("无法连接到服务器，请确保应用正在运行")
            return False
        except Exception as e:
            print_error(f"登录时发生错误: {e}")
            return False
    
    def test_generate_single_code(self):
        """测试生成单个邀请码"""
        print_test("生成单个邀请码")
        
        try:
            response = self.session.post(
                f'{self.base_url}/api/admin/invitation-codes/generate',
                json={'count': 1},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    code_data = data['data']
                    print_success(f"生成成功: {code_data.get('code_display', code_data.get('code'))}")
                    print_info(f"  邀请码ID: {code_data.get('id')}")
                    print_info(f"  原始码: {code_data.get('code')}")
                    print_info(f"  格式化: {code_data.get('code_display')}")
                    return code_data.get('code')
                else:
                    print_error(f"生成失败: {data.get('message')}")
                    return None
            else:
                print_error(f"请求失败，状态码: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print_error(f"生成邀请码时发生错误: {e}")
            return None
    
    def test_generate_batch_codes(self, count=5):
        """测试批量生成邀请码"""
        print_test(f"批量生成邀请码（{count}个）")
        
        try:
            response = self.session.post(
                f'{self.base_url}/api/admin/invitation-codes/generate',
                json={'count': count},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    codes = data['data'].get('codes', [])
                    print_success(f"批量生成成功: {len(codes)} 个邀请码")
                    for i, code_data in enumerate(codes, 1):
                        print_info(f"  {i}. {code_data.get('code_display', code_data.get('code'))}")
                    return [c.get('code') for c in codes]
                else:
                    print_error(f"批量生成失败: {data.get('message')}")
                    return []
            else:
                print_error(f"请求失败，状态码: {response.status_code}")
                print(response.text)
                return []
                
        except Exception as e:
            print_error(f"批量生成邀请码时发生错误: {e}")
            return []
    
    def test_get_code_list(self, status='all'):
        """测试获取邀请码列表"""
        print_test(f"获取邀请码列表（状态: {status}）")
        
        try:
            response = self.session.get(
                f'{self.base_url}/api/admin/invitation-codes/list',
                params={'status': status, 'page': 1, 'per_page': 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    codes = data['data'].get('codes', [])
                    pagination = data['data'].get('pagination', {})
                    print_success(f"获取成功: {len(codes)} 个邀请码")
                    print_info(f"  总数: {pagination.get('total', 0)}")
                    print_info(f"  当前页: {pagination.get('page', 1)}")
                    print_info(f"  总页数: {pagination.get('total_pages', 0)}")
                    
                    # 显示前5个
                    for i, code in enumerate(codes[:5], 1):
                        status_text = "已使用" if code.get('is_used') else "未使用"
                        print_info(f"  {i}. {code.get('code_display')} - {status_text}")
                    
                    return codes
                else:
                    print_error(f"获取失败: {data.get('message')}")
                    return []
            else:
                print_error(f"请求失败，状态码: {response.status_code}")
                print(response.text)
                return []
                
        except Exception as e:
            print_error(f"获取邀请码列表时发生错误: {e}")
            return []
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        print_test("获取邀请码统计信息")
        
        try:
            response = self.session.get(
                f'{self.base_url}/api/admin/invitation-codes/statistics'
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data['data']
                    print_success("获取统计信息成功")
                    print_info(f"  总数: {stats.get('total', 0)}")
                    print_info(f"  已使用: {stats.get('used', 0)}")
                    print_info(f"  未使用: {stats.get('unused', 0)}")
                    print_info(f"  使用率: {stats.get('usage_rate', 0):.2f}%")
                    return stats
                else:
                    print_error(f"获取失败: {data.get('message')}")
                    return None
            else:
                print_error(f"请求失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            print_error(f"获取统计信息时发生错误: {e}")
            return None
    
    def test_validate_code(self, code):
        """测试验证邀请码（注册API内部会调用，这里单独测试）"""
        print_test(f"验证邀请码: {code[:10]}...")
        
        # 注意：这个功能是通过注册API间接测试的
        # 我们会在注册测试中验证
        print_info("邀请码验证将在注册测试中进行")
        return True
    
    def test_register_with_invitation_code(self, invitation_code):
        """测试使用邀请码注册"""
        print_test(f"使用邀请码注册新用户")
        
        # 生成唯一的用户名和邮箱
        timestamp = int(datetime.now().timestamp())
        test_username = f"testuser_{timestamp}"
        test_email = f"test_{timestamp}@example.com"
        
        register_data = {
            'username': test_username,
            'email': test_email,
            'password': 'test123456',
            'confirm_password': 'test123456',
            'nickname': '测试用户',
            'invitation_code': invitation_code
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/register',
                json=register_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print_success(f"注册成功: {test_username}")
                    user_data = data['data'].get('user', {})
                    print_info(f"  用户ID: {user_data.get('id')}")
                    print_info(f"  用户名: {user_data.get('username')}")
                    print_info(f"  邮箱: {user_data.get('email')}")
                    return True
                else:
                    print_error(f"注册失败: {data.get('message')}")
                    return False
            else:
                print_error(f"注册失败，状态码: {response.status_code}")
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                print_error(f"错误信息: {data.get('message', response.text)}")
                return False
                
        except Exception as e:
            print_error(f"注册时发生错误: {e}")
            return False
    
    def test_register_with_invalid_code(self):
        """测试使用无效邀请码注册（应该失败）"""
        print_test("使用无效邀请码注册（应该失败）")
        
        register_data = {
            'username': 'test_invalid',
            'email': 'test_invalid@example.com',
            'password': 'test123456',
            'confirm_password': 'test123456',
            'invitation_code': 'INVALIDCODE123456'
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/register',
                json=register_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                data = response.json()
                if not data.get('success'):
                    print_success(f"正确拒绝无效邀请码: {data.get('message')}")
                    return True
                else:
                    print_error("应该拒绝无效邀请码，但注册成功了")
                    return False
            else:
                print_error(f"应该返回400，但返回了 {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"测试时发生错误: {e}")
            return False
    
    def test_register_without_code(self):
        """测试不提供邀请码注册（应该失败）"""
        print_test("不提供邀请码注册（应该失败）")
        
        register_data = {
            'username': 'test_no_code',
            'email': 'test_no_code@example.com',
            'password': 'test123456',
            'confirm_password': 'test123456'
            # 故意不提供invitation_code
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/register',
                json=register_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                data = response.json()
                if not data.get('success'):
                    print_success(f"正确要求邀请码: {data.get('message')}")
                    return True
                else:
                    print_error("应该要求邀请码，但注册成功了")
                    return False
            else:
                print_error(f"应该返回400，但返回了 {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"测试时发生错误: {e}")
            return False
    
    def test_export_unused_codes(self):
        """测试导出未使用的邀请码"""
        print_test("导出未使用的邀请码（CSV）")
        
        try:
            response = self.session.get(
                f'{self.base_url}/api/admin/invitation-codes/export/unused'
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'csv' in content_type.lower() or 'text/csv' in content_type:
                    print_success("导出成功（CSV格式）")
                    print_info(f"  文件大小: {len(response.content)} 字节")
                    print_info(f"  内容类型: {content_type}")
                    # 显示前几行
                    lines = response.text.split('\n')[:5]
                    print_info("  前几行内容:")
                    for line in lines:
                        if line.strip():
                            print_info(f"    {line}")
                    return True
                else:
                    print_error(f"导出格式错误: {content_type}")
                    return False
            else:
                print_error(f"导出失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"导出时发生错误: {e}")
            return False
    
    def test_permission_check(self):
        """测试权限检查（非管理员应该无法访问）"""
        print_test("测试权限检查（普通用户不能生成邀请码）")
        
        # 创建一个普通用户session（如果有的话）
        # 这里我们直接测试API，因为需要先注册普通用户
        print_info("权限检查已在@super_admin_required装饰器中实现")
        print_info("需要手动测试：使用普通用户token访问应该返回403")
        return True


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  邀请码系统API测试")
    print("=" * 60)
    
    tester = APITester()
    
    # 1. 登录测试
    print_section("1. 管理员登录测试")
    if not tester.login_as_admin():
        print_error("管理员登录失败，无法继续测试")
        print_warning("请确保应用正在运行，并且admin用户存在（用户名: admin, 密码: admin123456）")
        return
    
    # 2. 生成邀请码测试
    print_section("2. 生成邀请码测试")
    single_code = tester.test_generate_single_code()
    batch_codes = tester.test_generate_batch_codes(5)
    
    # 验证批量生成限制
    print_test("测试批量生成限制（超过10个应该失败）")
    invalid_response = tester.session.post(
        f'{BASE_URL}/api/admin/invitation-codes/generate',
        json={'count': 15},
        headers={'Content-Type': 'application/json'}
    )
    if invalid_response.status_code == 400:
        print_success("正确限制批量生成数量（超过10个被拒绝）")
    else:
        print_error("应该限制批量生成数量")
    
    # 3. 获取邀请码列表测试
    print_section("3. 获取邀请码列表测试")
    tester.test_get_code_list('all')
    tester.test_get_code_list('unused')
    tester.test_get_code_list('used')
    
    # 4. 统计信息测试
    print_section("4. 统计信息测试")
    tester.test_get_statistics()
    
    # 5. 注册测试
    print_section("5. 注册功能测试")
    if single_code:
        print_test("测试正常注册流程")
        tester.test_register_with_invitation_code(single_code)
    else:
        print_warning("无法测试注册，因为没有有效的邀请码")
    
    # 测试无效邀请码
    tester.test_register_with_invalid_code()
    
    # 测试缺少邀请码
    tester.test_register_without_code()
    
    # 6. 导出测试
    print_section("6. 导出功能测试")
    tester.test_export_unused_codes()
    
    # 7. 权限测试
    print_section("7. 权限检查测试")
    tester.test_permission_check()
    
    # 总结
    print_section("测试总结")
    print_success("API测试完成！")
    print_info("请检查上述测试结果，确保所有功能正常")
    print_warning("注意：需要确保数据库表已创建（运行迁移或创建表）")


if __name__ == "__main__":
    main()

