#!/usr/bin/env python3
"""
数据层完整性测试脚本
测试Repository和Service层的所有功能
"""
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.repositories.user_repository import UserRepository
from app.repositories.stock_repository import StockRepository
from app.repositories.watchlist_repository import WatchlistRepository
from app.services.data.user_service import UserDataService
from app.services.data.stock_service import StockDataService


class DataLayerTester:
    """数据层测试器"""
    
    def __init__(self):
        self.app = create_app('testing')
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始数据层完整性测试...\n")
        
        with self.app.app_context():
            # 初始化测试数据库
            self._setup_test_database()
            
            # 测试Repository层
            self._test_repositories()
            
            # 测试Service层
            self._test_services()
            
            # 测试数据完整性
            self._test_data_integrity()
            
            # 清理测试数据
            self._cleanup_test_database()
        
        self._print_summary()
    
    def _setup_test_database(self):
        """设置测试数据库"""
        print("📊 设置测试数据库...")
        db.create_all()
        
        # 创建测试股票数据
        from app.services.data.database_service import DatabaseService
        db_service = DatabaseService(db.session)
        db_service.populate_stock_pools()
        print("✅ 测试数据库设置完成\n")
    
    def _cleanup_test_database(self):
        """清理测试数据库"""
        print("🧹 清理测试数据...")
        db.drop_all()
        print("✅ 测试数据清理完成\n")
    
    def _test_repositories(self):
        """测试Repository层"""
        print("🏗️ 测试Repository层...")
        
        # 测试用户Repository
        self._test_user_repository()
        
        # 测试股票Repository
        self._test_stock_repository()
        
        # 测试关注列表Repository
        self._test_watchlist_repository()
        
        print("✅ Repository层测试完成\n")
    
    def _test_user_repository(self):
        """测试用户Repository"""
        print("  👤 测试UserRepository...")
        
        user_repo = UserRepository(db.session)
        
        # 测试创建用户
        try:
            user = user_repo.create_user('test@example.com', 'Test User')
            self._assert(user is not None, "用户创建失败")
            self._assert(user.email == 'test@example.com', "用户邮箱不匹配")
            self._assert(user.nickname == 'Test User', "用户昵称不匹配")
            self._assert(user.plan_type == 'TRIAL', "默认计划类型不正确")
            self._assert(user.remaining_quota == 1, "默认剩余额度不正确")
            print("    ✅ 用户创建测试通过")
        except Exception as e:
            self._record_error("用户创建测试", e)
        
        # 测试根据邮箱查找用户
        try:
            found_user = user_repo.get_by_email('test@example.com')
            self._assert(found_user is not None, "根据邮箱查找用户失败")
            self._assert(found_user.id == user.id, "查找到的用户ID不匹配")
            print("    ✅ 根据邮箱查找用户测试通过")
        except Exception as e:
            self._record_error("根据邮箱查找用户测试", e)
        
        # 测试更新用户额度
        try:
            updated_user = user_repo.update_quota(user.id, 5)
            self._assert(updated_user is not None, "更新用户额度失败")
            self._assert(updated_user.remaining_quota == 5, "用户额度更新不正确")
            print("    ✅ 更新用户额度测试通过")
        except Exception as e:
            self._record_error("更新用户额度测试", e)
        
        # 测试升级用户计划
        try:
            upgraded_user = user_repo.update_plan(user.id, 'SUBSCRIPTION', 999)
            self._assert(upgraded_user is not None, "升级用户计划失败")
            self._assert(upgraded_user.plan_type == 'SUBSCRIPTION', "用户计划类型不正确")
            self._assert(upgraded_user.remaining_quota == 999, "用户额度不正确")
            print("    ✅ 升级用户计划测试通过")
        except Exception as e:
            self._record_error("升级用户计划测试", e)
    
    def _test_stock_repository(self):
        """测试股票Repository"""
        print("  📈 测试StockRepository...")
        
        stock_repo = StockRepository(db.session)
        
        # 测试股票总数
        try:
            total_count = stock_repo.count()
            self._assert(total_count == 200, f"股票总数不正确，期望200，实际{total_count}")
            print("    ✅ 股票总数测试通过")
        except Exception as e:
            self._record_error("股票总数测试", e)
        
        # 测试根据代码查找股票
        try:
            apple_stock = stock_repo.get_by_code('AAPL')
            self._assert(apple_stock is not None, "根据代码查找AAPL失败")
            self._assert(apple_stock.name == '苹果公司', "AAPL股票名称不正确")
            self._assert(apple_stock.market == 'US', "AAPL市场不正确")
            print("    ✅ 根据代码查找股票测试通过")
        except Exception as e:
            self._record_error("根据代码查找股票测试", e)
        
        # 测试股票搜索
        try:
            search_results = stock_repo.search_stocks('苹果')
            self._assert(len(search_results) > 0, "搜索'苹果'没有结果")
            found_apple = any(stock.code == 'AAPL' for stock in search_results)
            self._assert(found_apple, "搜索结果中没有找到AAPL")
            print("    ✅ 股票搜索测试通过")
        except Exception as e:
            self._record_error("股票搜索测试", e)
        
        # 测试按市场获取股票
        try:
            us_stocks = stock_repo.get_by_market('US')
            hk_stocks = stock_repo.get_by_market('HK')
            self._assert(len(us_stocks) == 100, f"美股数量不正确，期望100，实际{len(us_stocks)}")
            self._assert(len(hk_stocks) == 100, f"港股数量不正确，期望100，实际{len(hk_stocks)}")
            print("    ✅ 按市场获取股票测试通过")
        except Exception as e:
            self._record_error("按市场获取股票测试", e)
        
        # 测试创建自定义股票
        try:
            custom_stock = stock_repo.create_stock(
                'TEST', '测试公司', 'US', 'USER_ADDED',
                exchange='NASDAQ', industry='测试行业', market_cap=1000000000
            )
            self._assert(custom_stock is not None, "创建自定义股票失败")
            self._assert(custom_stock.code == 'TEST', "自定义股票代码不正确")
            self._assert(custom_stock.stock_type == 'USER_ADDED', "自定义股票类型不正确")
            print("    ✅ 创建自定义股票测试通过")
        except Exception as e:
            self._record_error("创建自定义股票测试", e)
    
    def _test_watchlist_repository(self):
        """测试关注列表Repository"""
        print("  ⭐ 测试WatchlistRepository...")
        
        user_repo = UserRepository(db.session)
        stock_repo = StockRepository(db.session)
        watchlist_repo = WatchlistRepository(db.session)
        
        # 创建测试用户
        test_user = user_repo.create_user('watchlist@example.com', 'Watchlist User')
        
        # 获取测试股票
        apple_stock = stock_repo.get_by_code('AAPL')
        tencent_stock = stock_repo.get_by_code('00700')
        
        # 测试添加到关注列表
        try:
            watchlist_item1 = watchlist_repo.add_to_watchlist(test_user.id, apple_stock.id)
            self._assert(watchlist_item1 is not None, "添加AAPL到关注列表失败")
            
            watchlist_item2 = watchlist_repo.add_to_watchlist(test_user.id, tencent_stock.id)
            self._assert(watchlist_item2 is not None, "添加腾讯到关注列表失败")
            print("    ✅ 添加到关注列表测试通过")
        except Exception as e:
            self._record_error("添加到关注列表测试", e)
        
        # 测试获取用户关注列表
        try:
            user_watchlist = watchlist_repo.get_user_watchlist(test_user.id)
            self._assert(len(user_watchlist) == 2, f"用户关注列表数量不正确，期望2，实际{len(user_watchlist)}")
            print("    ✅ 获取用户关注列表测试通过")
        except Exception as e:
            self._record_error("获取用户关注列表测试", e)
        
        # 测试获取用户关注列表（含股票详情）
        try:
            watchlist_with_stocks = watchlist_repo.get_user_watchlist_with_stocks(test_user.id)
            self._assert(len(watchlist_with_stocks) == 2, "关注列表详情数量不正确")
            
            stock_codes = [item['stock']['code'] for item in watchlist_with_stocks]
            self._assert('AAPL' in stock_codes, "关注列表中没有AAPL")
            self._assert('00700' in stock_codes, "关注列表中没有腾讯")
            print("    ✅ 获取关注列表详情测试通过")
        except Exception as e:
            self._record_error("获取关注列表详情测试", e)
        
        # 测试关注数量限制
        try:
            # 检查当前关注数量
            current_count = watchlist_repo.get_watchlist_count(test_user.id)
            print(f"      当前关注数量: {current_count}")
            
            # 添加股票直到达到20支限制
            remaining_slots = 20 - current_count
            all_stocks = stock_repo.get_by_market('US') + stock_repo.get_by_market('HK')
            
            # 获取当前已关注的股票ID
            current_watchlist = watchlist_repo.get_user_watchlist(test_user.id)
            watched_stock_ids = {item.stock_id for item in current_watchlist}
            
            # 选择未关注的股票
            available_stocks = [stock for stock in all_stocks if stock.id not in watched_stock_ids]
            stocks_to_add = available_stocks[:remaining_slots]
            
            print(f"      需要添加 {remaining_slots} 支股票")
            for stock in stocks_to_add:
                watchlist_repo.add_to_watchlist(test_user.id, stock.id)
            
            # 验证已达到20支
            final_count = watchlist_repo.get_watchlist_count(test_user.id)
            print(f"      添加后关注数量: {final_count}")
            self._assert(final_count == 20, f"关注数量应该为20，实际为{final_count}")
            
            # 现在尝试添加第21支应该失败
            # 选择一支未关注的股票
            final_watchlist = watchlist_repo.get_user_watchlist(test_user.id)
            final_watched_ids = {item.stock_id for item in final_watchlist}
            remaining_stocks = [stock for stock in all_stocks if stock.id not in final_watched_ids]
            extra_stock = remaining_stocks[0] if remaining_stocks else None
            
            if not extra_stock:
                self._record_error("关注数量限制测试", "没有可用的额外股票进行测试")
                return
            try:
                watchlist_repo.add_to_watchlist(test_user.id, extra_stock.id)
                self._record_error("关注数量限制测试", "应该抛出异常但没有")
            except ValueError as ve:
                if "关注列表已满" in str(ve):
                    print("    ✅ 关注数量限制测试通过")
                else:
                    self._record_error("关注数量限制测试", f"异常信息不正确: {ve}")
        except Exception as e:
            self._record_error("关注数量限制测试", e)
        
        # 测试从关注列表移除
        try:
            removed = watchlist_repo.remove_from_watchlist(test_user.id, apple_stock.id)
            self._assert(removed == True, "从关注列表移除AAPL失败")
            
            remaining_count = watchlist_repo.get_watchlist_count(test_user.id)
            expected_count = 19  # 从20支移除1支后应该是19支
            self._assert(remaining_count == expected_count, f"移除后关注数量不正确，期望{expected_count}，实际{remaining_count}")
            print("    ✅ 从关注列表移除测试通过")
        except Exception as e:
            self._record_error("从关注列表移除测试", e)
    
    def _test_services(self):
        """测试Service层"""
        print("🔧 测试Service层...")
        
        # 测试用户Service
        self._test_user_service()
        
        # 测试股票Service
        self._test_stock_service()
        
        print("✅ Service层测试完成\n")
    
    def _test_user_service(self):
        """测试用户Service"""
        print("  👥 测试UserDataService...")
        
        user_service = UserDataService(db.session)
        
        # 测试认证或创建用户
        try:
            # 新用户应该被创建
            user1 = user_service.authenticate_or_create_user('newuser@example.com')
            self._assert(user1 is not None, "认证或创建新用户失败")
            self._assert(user1.email == 'newuser@example.com', "新用户邮箱不正确")
            
            # 已存在用户应该被返回
            user2 = user_service.authenticate_or_create_user('newuser@example.com')
            self._assert(user2.id == user1.id, "认证已存在用户失败")
            print("    ✅ 认证或创建用户测试通过")
        except Exception as e:
            self._record_error("认证或创建用户测试", e)
        
        # 测试获取用户资料
        try:
            profile = user_service.get_user_profile(user1.id)
            self._assert(profile is not None, "获取用户资料失败")
            self._assert(profile['email'] == 'newuser@example.com', "用户资料邮箱不正确")
            self._assert('plan_type' in profile, "用户资料缺少计划类型")
            print("    ✅ 获取用户资料测试通过")
        except Exception as e:
            self._record_error("获取用户资料测试", e)
        
        # 测试消费额度
        try:
            initial_quota = user1.remaining_quota
            success = user_service.consume_quota(user1.id, 1)
            self._assert(success == True, "消费额度失败")
            
            # 刷新用户数据
            db.session.refresh(user1)
            self._assert(user1.remaining_quota == initial_quota - 1, "额度消费后数量不正确")
            print("    ✅ 消费额度测试通过")
        except Exception as e:
            self._record_error("消费额度测试", e)
        
        # 测试添加额度
        try:
            current_quota = user1.remaining_quota
            updated_user = user_service.add_quota(user1.id, 5)
            self._assert(updated_user is not None, "添加额度失败")
            self._assert(updated_user.remaining_quota == current_quota + 5, "添加额度后数量不正确")
            print("    ✅ 添加额度测试通过")
        except Exception as e:
            self._record_error("添加额度测试", e)
    
    def _test_stock_service(self):
        """测试股票Service"""
        print("  📊 测试StockDataService...")
        
        user_service = UserDataService(db.session)
        stock_service = StockDataService(db.session)
        
        # 创建测试用户
        test_user = user_service.authenticate_or_create_user('stockservice@example.com')
        
        # 测试获取股票池
        try:
            stock_pools = stock_service.get_stock_pools()
            self._assert('us_stocks' in stock_pools, "股票池缺少美股数据")
            self._assert('hk_stocks' in stock_pools, "股票池缺少港股数据")
            self._assert(len(stock_pools['us_stocks']) == 100, "美股数量不正确")
            self._assert(len(stock_pools['hk_stocks']) == 100, "港股数量不正确")
            self._assert(stock_pools['total_count'] == 200, "股票池总数不正确")
            print("    ✅ 获取股票池测试通过")
        except Exception as e:
            self._record_error("获取股票池测试", e)
        
        # 测试股票搜索
        try:
            search_results = stock_service.search_stocks('苹果', user_id=test_user.id)
            self._assert(len(search_results) > 0, "搜索股票没有结果")
            
            apple_found = any(stock['code'] == 'AAPL' for stock in search_results)
            self._assert(apple_found, "搜索结果中没有找到苹果股票")
            
            # 检查是否包含关注状态
            self._assert('is_watching' in search_results[0], "搜索结果缺少关注状态")
            print("    ✅ 股票搜索测试通过")
        except Exception as e:
            self._record_error("股票搜索测试", e)
        
        # 测试添加到关注列表
        try:
            result = stock_service.add_to_watchlist(test_user.id, 'AAPL')
            self._assert(result['success'] == True, "添加AAPL到关注列表失败")
            
            # 测试重复添加
            result2 = stock_service.add_to_watchlist(test_user.id, 'AAPL')
            self._assert(result2['success'] == True, "重复添加应该成功（返回已存在项）")
            print("    ✅ 添加到关注列表测试通过")
        except Exception as e:
            self._record_error("添加到关注列表测试", e)
        
        # 测试获取用户关注列表
        try:
            watchlist_data = stock_service.get_user_watchlist(test_user.id)
            self._assert('watchlist' in watchlist_data, "关注列表数据格式错误")
            self._assert('count' in watchlist_data, "关注列表缺少计数")
            self._assert('remaining_slots' in watchlist_data, "关注列表缺少剩余名额")
            self._assert(watchlist_data['count'] == 1, "关注列表数量不正确")
            self._assert(watchlist_data['remaining_slots'] == 19, "剩余名额计算不正确")
            print("    ✅ 获取用户关注列表测试通过")
        except Exception as e:
            self._record_error("获取用户关注列表测试", e)
    
    def _test_data_integrity(self):
        """测试数据完整性"""
        print("🔍 测试数据完整性...")
        
        # 测试外键约束
        try:
            user_repo = UserRepository(db.session)
            stock_repo = StockRepository(db.session)
            watchlist_repo = WatchlistRepository(db.session)
            
            # 创建测试数据
            test_user = user_repo.create_user('integrity@example.com', 'Integrity User')
            apple_stock = stock_repo.get_by_code('AAPL')
            
            # 添加关注
            watchlist_item = watchlist_repo.add_to_watchlist(test_user.id, apple_stock.id)
            
            # 验证关系
            self._assert(watchlist_item.user_id == test_user.id, "用户外键关系不正确")
            self._assert(watchlist_item.stock_id == apple_stock.id, "股票外键关系不正确")
            print("    ✅ 外键约束测试通过")
        except Exception as e:
            self._record_error("外键约束测试", e)
        
        # 测试唯一约束
        try:
            # 尝试创建相同代码的股票
            try:
                stock_repo.create_stock('AAPL', '重复苹果', 'US')
                self._record_error("唯一约束测试", "应该抛出唯一约束异常但没有")
            except Exception:
                print("    ✅ 唯一约束测试通过")
        except Exception as e:
            self._record_error("唯一约束测试", e)
        
        # 测试数据类型和长度
        try:
            # 测试超长字符串
            try:
                stock_repo.create_stock(
                    'TOOLONG',
                    'A' * 300,  # 超过200字符限制
                    'US'
                )
                # 如果没有抛出异常，检查是否被截断
                long_stock = stock_repo.get_by_code('TOOLONG')
                if long_stock and len(long_stock.name) <= 200:
                    print("    ✅ 字符串长度限制测试通过（已截断）")
                else:
                    self._record_error("字符串长度限制测试", "超长字符串未被处理")
            except Exception:
                print("    ✅ 字符串长度限制测试通过（抛出异常）")
        except Exception as e:
            self._record_error("数据类型测试", e)
        
        print("✅ 数据完整性测试完成\n")
    
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
        print("📋 数据层测试总结")
        print("=" * 60)
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"📊 总计: {self.passed + self.failed}")
        
        if self.failed > 0:
            print(f"\n❌ 失败的测试:")
            for error in self.errors:
                print(f"   • {error}")
            print(f"\n🚨 数据层存在 {self.failed} 个问题，需要修复！")
        else:
            print(f"\n🎉 恭喜！数据层所有测试通过，代码质量良好！")
        
        success_rate = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        print(f"📈 成功率: {success_rate:.1f}%")


if __name__ == '__main__':
    tester = DataLayerTester()
    tester.run_all_tests()
