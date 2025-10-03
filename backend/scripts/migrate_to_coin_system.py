#!/usr/bin/env python3
"""
金币系统数据迁移脚本
从无金币版本迁移到金币版本

迁移内容：
1. 为所有现有用户创建金币账户
2. 根据用户历史使用情况分配初始金币
3. 创建金币交易记录
4. 保持所有现有数据不变

使用方法：
python scripts/migrate_to_coin_system.py [--dry-run] [--backup]
"""

import os
import sys
import argparse
import shutil
from datetime import datetime, date
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.user import User
from app.models.analysis import AnalysisTask
from app.models.coin import UserCoin, CoinTransaction, CoinPackage, CoinOrder, DailyBonus
from app.services.coin.coin_service import CoinService
from app.repositories.coin_repository import CoinRepository


class CoinSystemMigration:
    def __init__(self, dry_run=False, backup=True):
        self.dry_run = dry_run
        self.backup = backup
        self.app = create_app()
        self.migration_log = []
        
    def log(self, message):
        """记录迁移日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.migration_log.append(log_message)
    
    def create_backup(self):
        """创建数据库备份"""
        if not self.backup:
            return
            
        self.log("创建数据库备份...")
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"pre_coin_migration_{timestamp}.db"
        
        # 复制数据库文件
        db_path = Path("instance/equitycompass.db")
        if db_path.exists():
            shutil.copy2(db_path, backup_file)
            self.log(f"数据库备份已创建: {backup_file}")
        else:
            self.log("警告: 未找到数据库文件，跳过备份")
    
    def check_existing_coin_data(self):
        """检查是否已有金币数据"""
        with self.app.app_context():
            coin_count = UserCoin.query.count()
            if coin_count > 0:
                self.log(f"警告: 发现 {coin_count} 个现有金币账户")
                return True
            return False
    
    def create_coin_packages(self):
        """创建金币套餐数据"""
        self.log("创建金币套餐...")
        
        packages = [
            {
                'name': '每日免费',
                'description': '每日登录可获得20金币，可分析2个报告',
                'coins': 20,
                'price': 0.0,
                'original_price': None,
                'package_type': 'FREE',
                'is_active': True,
                'sort_order': 1
            },
            {
                'name': '小额包',
                'description': '100金币，可分析10个报告',
                'coins': 100,
                'price': 9.9,
                'original_price': 12.9,
                'package_type': 'SMALL',
                'is_active': True,
                'sort_order': 2
            },
            {
                'name': '中额包',
                'description': '500金币，可分析50个报告',
                'coins': 500,
                'price': 39.9,
                'original_price': 49.9,
                'package_type': 'MEDIUM',
                'is_active': True,
                'sort_order': 3
            },
            {
                'name': '大额包',
                'description': '1000金币，可分析100个报告',
                'coins': 1000,
                'price': 69.9,
                'original_price': 99.9,
                'package_type': 'LARGE',
                'is_active': True,
                'sort_order': 4
            },
            {
                'name': '超大包',
                'description': '2000金币，可分析200个报告',
                'coins': 2000,
                'price': 119.9,
                'original_price': 199.9,
                'package_type': 'XLARGE',
                'is_active': True,
                'sort_order': 5
            },
            {
                'name': '月度订阅',
                'description': '每日100金币，可分析10个报告/天',
                'coins': 100,
                'price': 19.9,
                'original_price': None,
                'package_type': 'SUBSCRIPTION',
                'is_active': True,
                'sort_order': 6
            },
            {
                'name': '年度订阅',
                'description': '每日120金币，可分析12个报告/天',
                'coins': 120,
                'price': 199.0,
                'original_price': None,
                'package_type': 'SUBSCRIPTION',
                'is_active': True,
                'sort_order': 7
            }
        ]
        
        if not self.dry_run:
            with self.app.app_context():
                for package_data in packages:
                    existing = CoinPackage.query.filter_by(name=package_data['name']).first()
                    if not existing:
                        package = CoinPackage(**package_data)
                        db.session.add(package)
                
                db.session.commit()
                self.log(f"已创建 {len(packages)} 个金币套餐")
        else:
            self.log(f"[DRY RUN] 将创建 {len(packages)} 个金币套餐")
    
    def calculate_initial_coins(self, user):
        """根据用户历史使用情况计算初始金币"""
        with self.app.app_context():
            # 基础金币：所有用户都获得
            base_coins = 20
            
            # 根据用户角色给予额外金币
            if user.user_role == 'SUPER_ADMIN':
                bonus_coins = 1000  # 超级管理员
            elif user.user_role == 'SITE_ADMIN':
                bonus_coins = 500   # 站点管理员
            else:
                bonus_coins = 0     # 普通用户
                
            # 根据注册时间给予老用户奖励
            if hasattr(user, 'created_at') and user.created_at:
                days_since_registration = (date.today() - user.created_at.date()).days
                if days_since_registration > 30:
                    bonus_coins += 50  # 老用户奖励
                elif days_since_registration > 7:
                    bonus_coins += 20  # 早期用户奖励
            
            # 根据历史分析任务数量给予奖励
            analysis_count = AnalysisTask.query.filter_by(user_id=user.id).count()
            if analysis_count > 0:
                bonus_coins += min(analysis_count * 5, 100)  # 每个历史分析任务5金币，最多100金币
            
            total_coins = base_coins + bonus_coins
            return total_coins, base_coins, bonus_coins
    
    def migrate_user_coins(self, user):
        """为单个用户创建金币账户"""
        total_coins, base_coins, bonus_coins = self.calculate_initial_coins(user)
        
        if not self.dry_run:
            with self.app.app_context():
                # 创建金币账户
                user_coin = UserCoin(
                    user_id=user.id,
                    total_coins=total_coins,
                    available_coins=total_coins,
                    frozen_coins=0
                )
                db.session.add(user_coin)
                db.session.flush()
                
                # 创建初始金币交易记录
                transaction = CoinTransaction(
                    user_coin_id=user_coin.id,
                    user_id=user.id,
                    transaction_type='EARN',
                    amount=total_coins,
                    balance_before=0,
                    balance_after=total_coins,
                    description=f'系统迁移奖励（基础{base_coins}金币 + 奖励{bonus_coins}金币）',
                    related_type='MIGRATION'
                )
                db.session.add(transaction)
                db.session.commit()
                
                self.log(f"用户 {user.username} (ID:{user.id}): 获得 {total_coins} 金币 (基础:{base_coins} + 奖励:{bonus_coins})")
        else:
            self.log(f"[DRY RUN] 用户 {user.username} (ID:{user.id}): 将获得 {total_coins} 金币 (基础:{base_coins} + 奖励:{bonus_coins})")
    
    def migrate_all_users(self):
        """迁移所有用户的金币账户"""
        self.log("开始迁移用户金币账户...")
        
        with self.app.app_context():
            users = User.query.filter_by(is_active=True).all()
            self.log(f"找到 {len(users)} 个活跃用户")
            
            for user in users:
                # 检查是否已有金币账户
                existing_coin = UserCoin.query.filter_by(user_id=user.id).first()
                if existing_coin:
                    self.log(f"用户 {user.username} 已有金币账户，跳过")
                    continue
                    
                self.migrate_user_coins(user)
        
        self.log("用户金币账户迁移完成")
    
    def verify_migration(self):
        """验证迁移结果"""
        self.log("验证迁移结果...")
        
        with self.app.app_context():
            total_users = User.query.filter_by(is_active=True).count()
            total_coin_accounts = UserCoin.query.count()
            total_transactions = CoinTransaction.query.count()
            total_packages = CoinPackage.query.count()
            
            self.log(f"验证结果:")
            self.log(f"  活跃用户数: {total_users}")
            self.log(f"  金币账户数: {total_coin_accounts}")
            self.log(f"  交易记录数: {total_transactions}")
            self.log(f"  金币套餐数: {total_packages}")
            
            if total_users == total_coin_accounts:
                self.log("✅ 迁移验证通过：所有用户都有金币账户")
            else:
                self.log("❌ 迁移验证失败：用户数和金币账户数不匹配")
                
            # 检查金币总额
            total_coins = db.session.query(db.func.sum(UserCoin.available_coins)).scalar() or 0
            self.log(f"  系统总金币数: {total_coins}")
    
    def save_migration_log(self):
        """保存迁移日志"""
        log_file = Path("migration_logs") / f"coin_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("金币系统迁移日志\n")
            f.write("=" * 50 + "\n")
            for log_entry in self.migration_log:
                f.write(log_entry + "\n")
        
        self.log(f"迁移日志已保存: {log_file}")
    
    def run_migration(self):
        """执行完整迁移流程"""
        self.log("开始金币系统数据迁移...")
        self.log(f"模式: {'DRY RUN' if self.dry_run else '正式迁移'}")
        
        try:
            # 1. 创建备份
            self.create_backup()
            
            # 2. 检查现有数据
            if self.check_existing_coin_data() and not self.dry_run:
                response = input("发现现有金币数据，是否继续？(y/N): ")
                if response.lower() != 'y':
                    self.log("迁移已取消")
                    return
            
            # 3. 创建金币套餐
            self.create_coin_packages()
            
            # 4. 迁移用户金币账户
            self.migrate_all_users()
            
            # 5. 验证迁移结果
            self.verify_migration()
            
            # 6. 保存日志
            self.save_migration_log()
            
            self.log("✅ 金币系统数据迁移完成！")
            
        except Exception as e:
            self.log(f"❌ 迁移过程中发生错误: {str(e)}")
            import traceback
            self.log(f"错误详情: {traceback.format_exc()}")
            raise


def main():
    parser = argparse.ArgumentParser(description='金币系统数据迁移脚本')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式，不实际修改数据')
    parser.add_argument('--no-backup', action='store_true', help='跳过数据库备份')
    
    args = parser.parse_args()
    
    migration = CoinSystemMigration(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    migration.run_migration()


if __name__ == '__main__':
    main()
