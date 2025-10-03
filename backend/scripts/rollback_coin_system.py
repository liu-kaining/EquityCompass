#!/usr/bin/env python3
"""
金币系统回滚脚本
用于在迁移失败时回滚到无金币版本

回滚内容：
1. 删除所有金币相关数据
2. 恢复数据库备份
3. 清理金币相关表

使用方法：
python scripts/rollback_coin_system.py [--backup-file BACKUP_FILE]
"""

import os
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.coin import UserCoin, CoinTransaction, CoinPackage, CoinOrder, DailyBonus


class CoinSystemRollback:
    def __init__(self, backup_file=None):
        self.backup_file = backup_file
        self.app = create_app()
        self.rollback_log = []
        
    def log(self, message):
        """记录回滚日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.rollback_log.append(log_message)
    
    def backup_current_data(self):
        """备份当前数据"""
        self.log("备份当前数据...")
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"pre_rollback_{timestamp}.db"
        
        db_path = Path("instance/equitycompass.db")
        if db_path.exists():
            shutil.copy2(db_path, backup_file)
            self.log(f"当前数据已备份: {backup_file}")
            return backup_file
        else:
            self.log("警告: 未找到数据库文件")
            return None
    
    def count_coin_data(self):
        """统计金币相关数据"""
        with self.app.app_context():
            user_coins = UserCoin.query.count()
            transactions = CoinTransaction.query.count()
            packages = CoinPackage.query.count()
            orders = CoinOrder.query.count()
            bonuses = DailyBonus.query.count()
            
            self.log(f"金币数据统计:")
            self.log(f"  用户金币账户: {user_coins}")
            self.log(f"  交易记录: {transactions}")
            self.log(f"  金币套餐: {packages}")
            self.log(f"  金币订单: {orders}")
            self.log(f"  每日签到记录: {bonuses}")
            
            return user_coins + transactions + packages + orders + bonuses
    
    def clear_coin_data(self):
        """清理所有金币相关数据"""
        self.log("清理金币相关数据...")
        
        with self.app.app_context():
            try:
                # 删除所有金币相关数据
                DailyBonus.query.delete()
                CoinOrder.query.delete()
                CoinTransaction.query.delete()
                UserCoin.query.delete()
                CoinPackage.query.delete()
                
                db.session.commit()
                self.log("✅ 金币相关数据已清理")
                
            except Exception as e:
                db.session.rollback()
                self.log(f"❌ 清理数据时发生错误: {str(e)}")
                raise
    
    def restore_database(self):
        """恢复数据库备份"""
        if not self.backup_file:
            self.log("未指定备份文件，跳过数据库恢复")
            return
            
        if not Path(self.backup_file).exists():
            self.log(f"❌ 备份文件不存在: {self.backup_file}")
            return
            
        self.log(f"恢复数据库备份: {self.backup_file}")
        
        db_path = Path("instance/equitycompass.db")
        if db_path.exists():
            # 备份当前数据库
            current_backup = self.backup_current_data()
            
            # 恢复备份
            shutil.copy2(self.backup_file, db_path)
            self.log("✅ 数据库已恢复")
        else:
            self.log("❌ 数据库文件不存在")
    
    def verify_rollback(self):
        """验证回滚结果"""
        self.log("验证回滚结果...")
        
        with self.app.app_context():
            try:
                # 检查金币表是否为空
                user_coins = UserCoin.query.count()
                transactions = CoinTransaction.query.count()
                packages = CoinPackage.query.count()
                
                if user_coins == 0 and transactions == 0 and packages == 0:
                    self.log("✅ 回滚验证通过：所有金币数据已清理")
                else:
                    self.log("❌ 回滚验证失败：仍有金币数据残留")
                    
            except Exception as e:
                self.log(f"❌ 验证过程中发生错误: {str(e)}")
    
    def save_rollback_log(self):
        """保存回滚日志"""
        log_file = Path("migration_logs") / f"coin_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("金币系统回滚日志\n")
            f.write("=" * 50 + "\n")
            for log_entry in self.rollback_log:
                f.write(log_entry + "\n")
        
        self.log(f"回滚日志已保存: {log_file}")
    
    def run_rollback(self):
        """执行回滚流程"""
        self.log("开始金币系统回滚...")
        
        try:
            # 1. 统计当前数据
            total_records = self.count_coin_data()
            
            if total_records == 0:
                self.log("没有金币数据需要回滚")
                return
            
            # 2. 确认回滚
            response = input(f"发现 {total_records} 条金币相关记录，确认要回滚吗？(y/N): ")
            if response.lower() != 'y':
                self.log("回滚已取消")
                return
            
            # 3. 清理金币数据
            self.clear_coin_data()
            
            # 4. 恢复数据库（如果指定了备份文件）
            self.restore_database()
            
            # 5. 验证回滚结果
            self.verify_rollback()
            
            # 6. 保存日志
            self.save_rollback_log()
            
            self.log("✅ 金币系统回滚完成！")
            
        except Exception as e:
            self.log(f"❌ 回滚过程中发生错误: {str(e)}")
            import traceback
            self.log(f"错误详情: {traceback.format_exc()}")
            raise


def main():
    parser = argparse.ArgumentParser(description='金币系统回滚脚本')
    parser.add_argument('--backup-file', help='指定要恢复的数据库备份文件')
    
    args = parser.parse_args()
    
    rollback = CoinSystemRollback(backup_file=args.backup_file)
    rollback.run_rollback()


if __name__ == '__main__':
    main()
