#!/usr/bin/env python3
"""
一键清除所有任务和报告数据
"""
import os
import shutil
import glob
from pathlib import Path

def clear_data():
    """清除所有数据"""
    print("🧹 开始清理数据...")
    
    # 清理目录
    dirs_to_clear = [
        'data/reports',
        'data/usage', 
        'data/exports',
        'data/logs',
        'data/tasks',
        'data/backups',
        'data/temp'
    ]
    
    for dir_path in dirs_to_clear:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"✅ 删除目录: {dir_path}")
        else:
            print(f"ℹ️  目录不存在: {dir_path}")
    
    # 清理数据库文件
    db_files = [
        'instance/equitycompass.db',
        'instance/dev.db', 
        'dev.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"✅ 删除数据库: {db_file}")
        else:
            print(f"ℹ️  数据库不存在: {db_file}")
    
    # 清理日志文件
    log_files = [
        'app.log',
        'celery.log',
        'error.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            os.remove(log_file)
            print(f"✅ 删除日志: {log_file}")
        else:
            print(f"ℹ️  日志不存在: {log_file}")
    
    # 清理任务文件
    task_files = glob.glob('data/reports/*.task.json')
    for task_file in task_files:
        os.remove(task_file)
        print(f"✅ 删除任务文件: {task_file}")
    
    print("🎉 数据清理完成！")

if __name__ == "__main__":
    confirm = input("⚠️  确定要清除所有数据吗？输入 'YES' 确认: ")
    if confirm.upper() == 'YES':
        clear_data()
    else:
        print("❌ 操作已取消")
