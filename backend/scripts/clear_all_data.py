#!/usr/bin/env python3
"""
一键清除所有任务和报告数据
用于数据清理和重置
"""
import os
import sys
import shutil
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清理器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.instance_dir = self.base_dir / 'instance'
        
        # 定义需要清理的目录和文件
        self.cleanup_targets = {
            'reports': self.data_dir / 'reports',
            'usage': self.data_dir / 'usage',
            'exports': self.data_dir / 'exports',
            'logs': self.data_dir / 'logs',
            'tasks': self.data_dir / 'tasks',
            'backups': self.data_dir / 'backups',
            'temp': self.data_dir / 'temp'
        }
        
        # 数据库文件
        self.db_files = [
            self.instance_dir / 'equitycompass.db',
            self.instance_dir / 'dev.db',
            self.base_dir / 'dev.db'
        ]
        
        # 日志文件
        self.log_files = [
            self.base_dir / 'app.log',
            self.base_dir / 'celery.log',
            self.base_dir / 'error.log'
        ]
    
    def confirm_cleanup(self) -> bool:
        """确认清理操作"""
        print("\n" + "="*60)
        print("⚠️  数据清理确认")
        print("="*60)
        print("此操作将清除以下数据：")
        print()
        
        # 显示将要清理的内容
        for name, path in self.cleanup_targets.items():
            if path.exists():
                if path.is_file():
                    size = path.stat().st_size
                    print(f"📄 {name}: {path} ({self._format_size(size)})")
                else:
                    file_count = len(list(path.rglob('*')))
                    print(f"📁 {name}: {path} ({file_count} 个文件)")
        
        # 显示数据库文件
        for db_file in self.db_files:
            if db_file.exists():
                size = db_file.stat().st_size
                print(f"🗄️  数据库: {db_file} ({self._format_size(size)})")
        
        # 显示日志文件
        for log_file in self.log_files:
            if log_file.exists():
                size = log_file.stat().st_size
                print(f"📝 日志: {log_file} ({self._format_size(size)})")
        
        print()
        print("⚠️  警告：此操作不可逆！")
        print()
        
        # 用户确认
        confirm = input("请输入 'YES' 确认清理所有数据: ").strip()
        return confirm.upper() == 'YES'
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def clear_directory(self, dir_path: Path, dir_name: str) -> bool:
        """清理目录"""
        try:
            if dir_path.exists():
                if dir_path.is_file():
                    dir_path.unlink()
                    logger.info(f"✅ 删除文件: {dir_name}")
                else:
                    shutil.rmtree(dir_path)
                    logger.info(f"✅ 删除目录: {dir_name}")
                return True
            else:
                logger.info(f"ℹ️  目录不存在，跳过: {dir_name}")
                return True
        except Exception as e:
            logger.error(f"❌ 删除失败 {dir_name}: {str(e)}")
            return False
    
    def clear_database(self, db_file: Path) -> bool:
        """清理数据库文件"""
        try:
            if db_file.exists():
                # 备份数据库（可选）
                backup_file = db_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                shutil.copy2(db_file, backup_file)
                logger.info(f"📋 备份数据库: {backup_file}")
                
                # 删除原数据库
                db_file.unlink()
                logger.info(f"✅ 删除数据库: {db_file}")
                return True
            else:
                logger.info(f"ℹ️  数据库不存在，跳过: {db_file}")
                return True
        except Exception as e:
            logger.error(f"❌ 删除数据库失败 {db_file}: {str(e)}")
            return False
    
    def clear_logs(self) -> bool:
        """清理日志文件"""
        success = True
        for log_file in self.log_files:
            try:
                if log_file.exists():
                    log_file.unlink()
                    logger.info(f"✅ 删除日志: {log_file}")
            except Exception as e:
                logger.error(f"❌ 删除日志失败 {log_file}: {str(e)}")
                success = False
        return success
    
    def clear_task_files(self) -> bool:
        """清理任务相关文件"""
        try:
            # 清理 .task.json 文件
            reports_dir = self.data_dir / 'reports'
            if reports_dir.exists():
                task_files = list(reports_dir.glob('*.task.json'))
                for task_file in task_files:
                    task_file.unlink()
                    logger.info(f"✅ 删除任务文件: {task_file.name}")
                
                logger.info(f"✅ 清理了 {len(task_files)} 个任务文件")
            return True
        except Exception as e:
            logger.error(f"❌ 清理任务文件失败: {str(e)}")
            return False
    
    def reset_database_schema(self) -> bool:
        """重置数据库结构（保留表结构，清空数据）"""
        try:
            # 找到最新的数据库文件
            db_file = None
            for db_path in self.db_files:
                if db_path.exists():
                    db_file = db_path
                    break
            
            if not db_file:
                logger.info("ℹ️  没有找到数据库文件，跳过数据库重置")
                return True
            
            logger.info(f"🗄️  重置数据库: {db_file}")
            
            # 连接数据库
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # 清空所有表数据
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':  # 跳过系统表
                    cursor.execute(f"DELETE FROM {table_name};")
                    logger.info(f"✅ 清空表: {table_name}")
            
            # 重置自增ID
            cursor.execute("DELETE FROM sqlite_sequence;")
            
            conn.commit()
            conn.close()
            
            logger.info("✅ 数据库数据重置完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 重置数据库失败: {str(e)}")
            return False
    
    def create_backup(self) -> bool:
        """创建数据备份"""
        try:
            backup_dir = self.data_dir / 'backups' / f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 备份数据目录
            if self.data_dir.exists():
                shutil.copytree(self.data_dir, backup_dir / 'data', dirs_exist_ok=True)
            
            # 备份数据库
            for db_file in self.db_files:
                if db_file.exists():
                    shutil.copy2(db_file, backup_dir / db_file.name)
            
            logger.info(f"📋 创建备份: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建备份失败: {str(e)}")
            return False
    
    def cleanup(self, create_backup: bool = True, reset_db: bool = False) -> bool:
        """执行完整的数据清理"""
        logger.info("🚀 开始数据清理...")
        
        # 创建备份
        if create_backup:
            if not self.create_backup():
                logger.warning("⚠️  备份创建失败，但继续清理")
        
        success = True
        
        # 清理目录
        for name, path in self.cleanup_targets.items():
            if not self.clear_directory(path, name):
                success = False
        
        # 清理任务文件
        if not self.clear_task_files():
            success = False
        
        # 清理日志文件
        if not self.clear_logs():
            success = False
        
        # 处理数据库
        if reset_db:
            # 重置数据库结构
            if not self.reset_database_schema():
                success = False
        else:
            # 删除数据库文件
            for db_file in self.db_files:
                if not self.clear_database(db_file):
                    success = False
        
        if success:
            logger.info("🎉 数据清理完成！")
        else:
            logger.error("❌ 数据清理过程中出现错误")
        
        return success
    
    def show_status(self):
        """显示当前数据状态"""
        print("\n" + "="*60)
        print("📊 当前数据状态")
        print("="*60)
        
        total_size = 0
        total_files = 0
        
        # 检查目录
        for name, path in self.cleanup_targets.items():
            if path.exists():
                if path.is_file():
                    size = path.stat().st_size
                    total_size += size
                    total_files += 1
                    print(f"📄 {name}: {self._format_size(size)}")
                else:
                    files = list(path.rglob('*'))
                    size = sum(f.stat().st_size for f in files if f.is_file())
                    total_size += size
                    total_files += len(files)
                    print(f"📁 {name}: {len(files)} 个文件, {self._format_size(size)}")
            else:
                print(f"❌ {name}: 不存在")
        
        # 检查数据库
        for db_file in self.db_files:
            if db_file.exists():
                size = db_file.stat().st_size
                total_size += size
                total_files += 1
                print(f"🗄️  数据库: {self._format_size(size)}")
        
        # 检查日志
        for log_file in self.log_files:
            if log_file.exists():
                size = log_file.stat().st_size
                total_size += size
                total_files += 1
                print(f"📝 日志: {self._format_size(size)}")
        
        print("-" * 60)
        print(f"📊 总计: {total_files} 个文件, {self._format_size(total_size)}")

def main():
    """主函数"""
    print("🧹 EquityCompass 数据清理工具")
    print("=" * 60)
    
    cleaner = DataCleaner()
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='EquityCompass 数据清理工具')
    parser.add_argument('--status', action='store_true', help='显示当前数据状态')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份')
    parser.add_argument('--reset-db', action='store_true', help='重置数据库结构（保留表，清空数据）')
    parser.add_argument('--force', action='store_true', help='强制清理，不询问确认')
    
    args = parser.parse_args()
    
    if args.status:
        cleaner.show_status()
        return
    
    # 确认清理
    if not args.force and not cleaner.confirm_cleanup():
        print("❌ 操作已取消")
        return
    
    # 执行清理
    success = cleaner.cleanup(
        create_backup=not args.no_backup,
        reset_db=args.reset_db
    )
    
    if success:
        print("\n✅ 数据清理完成！")
        print("💡 提示：如果需要重新初始化数据库，请运行：")
        print("   python scripts/init_db.py")
        print("   python scripts/import_stocks.py")
    else:
        print("\n❌ 数据清理失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
