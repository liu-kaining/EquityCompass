#!/usr/bin/env python3
"""
重新创建报告索引表
"""
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.analysis import ReportIndex, ReportStatistics, ReportViewLog, ReportDownloadLog
from app.models.stock import Stock

def recreate_report_index():
    """重新创建报告索引表"""
    app = create_app()
    
    with app.app_context():
        print("开始重新创建报告索引表...")
        
        # 清空所有相关表
        print("清空现有数据...")
        ReportDownloadLog.query.delete()
        ReportViewLog.query.delete()
        ReportStatistics.query.delete()
        ReportIndex.query.delete()
        db.session.commit()
        print("现有数据已清空")
        
        reports_dir = 'data/reports'
        registered_count = 0
        error_count = 0
        
        if not os.path.exists(reports_dir):
            print(f"报告目录不存在: {reports_dir}")
            return
        
        # 遍历所有日期目录
        for date_dir in sorted(os.listdir(reports_dir)):
            date_path = os.path.join(reports_dir, date_dir)
            if not os.path.isdir(date_path):
                continue
            
            print(f"处理日期目录: {date_dir}")
            
            # 遍历该日期目录下的所有报告文件
            for filename in os.listdir(date_path):
                if not filename.endswith('.json'):
                    continue
                
                report_file = os.path.join(date_path, filename)
                print(f"  处理文件: {filename}")
                
                try:
                    # 读取报告文件
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    
                    # 获取股票代码
                    stock_code = report_data.get('stock_code', '')
                    if not stock_code:
                        print(f"    跳过：没有股票代码")
                        continue
                    
                    # 查找股票
                    stock = Stock.query.filter_by(code=stock_code).first()
                    if not stock:
                        print(f"    跳过：未找到股票 {stock_code}")
                        continue
                    
                    # 处理分析日期
                    analysis_date_str = report_data.get('analysis_date', date_dir)
                    if isinstance(analysis_date_str, str):
                        try:
                            analysis_date = datetime.strptime(analysis_date_str, '%Y-%m-%d').date()
                        except ValueError:
                            # 如果日期格式不正确，使用目录名
                            analysis_date = datetime.strptime(date_dir, '%Y-%m-%d').date()
                    else:
                        analysis_date = analysis_date_str
                    
                    # 创建报告索引记录
                    report_index = ReportIndex(
                        stock_id=stock.id,
                        analysis_date=analysis_date,
                        file_path=report_file,
                        summary=report_data.get('content', '')[:500] if report_data.get('content') else '',
                        generated_at=datetime.utcnow()
                    )
                    
                    db.session.add(report_index)
                    db.session.commit()
                    
                    print(f"    ✅ 成功注册：{stock_code} - {analysis_date}")
                    registered_count += 1
                    
                except Exception as e:
                    print(f"    ❌ 错误：{str(e)}")
                    error_count += 1
                    db.session.rollback()
        
        print(f"\n重新创建完成！")
        print(f"成功注册: {registered_count} 个报告")
        print(f"错误: {error_count} 个报告")

if __name__ == "__main__":
    recreate_report_index()
