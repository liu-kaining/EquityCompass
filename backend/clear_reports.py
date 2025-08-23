#!/usr/bin/env python3
"""
删除所有分析报告
"""
import os
import shutil
from app import create_app, db
from app.models.analysis import AnalysisTask, ReportIndex

def clear_all_reports():
    app = create_app()
    with app.app_context():
        print("=== 删除所有分析报告 ===")
        
        # 1. 删除数据库中的报告记录
        print("1. 删除数据库中的报告记录...")
        deleted_tasks = AnalysisTask.query.delete()
        deleted_reports = ReportIndex.query.delete()
        db.session.commit()
        print(f"   删除了 {deleted_tasks} 个分析任务")
        print(f"   删除了 {deleted_reports} 个报告索引")
        
        # 2. 删除报告文件目录
        print("2. 删除报告文件目录...")
        reports_dir = 'data/reports'
        if os.path.exists(reports_dir):
            shutil.rmtree(reports_dir)
            print(f"   删除了报告目录: {reports_dir}")
        else:
            print(f"   报告目录不存在: {reports_dir}")
        
        # 3. 重新创建空的报告目录
        print("3. 重新创建报告目录...")
        os.makedirs(reports_dir, exist_ok=True)
        print(f"   创建了新的报告目录: {reports_dir}")
        
        # 4. 验证清理结果
        print("4. 验证清理结果...")
        remaining_tasks = AnalysisTask.query.count()
        remaining_reports = ReportIndex.query.count()
        print(f"   剩余分析任务: {remaining_tasks}")
        print(f"   剩余报告索引: {remaining_reports}")
        
        if os.path.exists(reports_dir):
            report_files = []
            for root, dirs, files in os.walk(reports_dir):
                for file in files:
                    if file.endswith('.json'):
                        report_files.append(os.path.join(root, file))
            print(f"   剩余报告文件: {len(report_files)}")
        else:
            print("   报告目录不存在")
        
        print("\n✅ 所有分析报告已清理完成！")
        print("现在可以开始正式产出报告了。")

if __name__ == "__main__":
    clear_all_reports()
