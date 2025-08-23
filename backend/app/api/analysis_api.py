"""
AI分析API
"""
from flask import Blueprint, request, session, jsonify
from app.utils.response import success_response, error_response
from app.services.ai.analysis_service import AnalysisService
from app import db
import logging

logger = logging.getLogger(__name__)
analysis_api_bp = Blueprint('analysis_api', __name__)

def get_analysis_service():
    """获取分析服务实例"""
    return AnalysisService(db.session)

@analysis_api_bp.route('/analyze', methods=['POST'])
def analyze_stock():
    """分析股票"""
    try:
        # 检查用户登录状态
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        # 获取请求数据
        data = request.get_json()
        stock_code = data.get('stock_code', '').strip().upper()
        analysis_type = data.get('analysis_type', 'default')  # default, fundamental, technical
        
        if not stock_code:
            return error_response("股票代码不能为空")
        
        # 运行分析
        service = get_analysis_service()
        result = service.run_analysis(stock_code, user_id, analysis_type)
        
        if result['success']:
            return success_response(
                data=result['report'],
                message=f"已生成 {stock_code} 的分析报告"
            )
        else:
            return error_response(result['error'])
        
    except Exception as e:
        logger.error(f"分析股票失败: {str(e)}")
        return error_response("分析股票失败", str(e))

@analysis_api_bp.route('/reports', methods=['GET'])
def get_user_reports():
    """获取用户的分析报告列表"""
    try:
        # 检查用户登录状态
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        # 获取查询参数
        limit = request.args.get('limit', 20, type=int)
        
        # 获取用户报告
        service = get_analysis_service()
        reports = service.get_user_reports(user_id, limit)
        
        return success_response(data={
            'reports': reports,
            'count': len(reports)
        })
        
    except Exception as e:
        logger.error(f"获取用户报告失败: {str(e)}")
        return error_response("获取报告失败", str(e))

@analysis_api_bp.route('/reports/<stock_code>', methods=['GET'])
def get_stock_report(stock_code):
    """获取指定股票的分析报告"""
    try:
        # 检查用户登录状态
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        # 获取查询参数
        date = request.args.get('date')  # 可选，默认为今天
        
        # 获取报告
        service = get_analysis_service()
        report = service.get_analysis_report(stock_code, date)
        
        if report:
            return success_response(data=report)
        else:
            return error_response("报告不存在")
        
    except Exception as e:
        logger.error(f"获取股票报告失败: {str(e)}")
        return error_response("获取报告失败", str(e))

@analysis_api_bp.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    """批量分析用户关注的股票"""
    try:
        # 检查用户登录状态
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        # 获取用户关注的股票
        from app.services.data.stock_service import StockDataService
        stock_service = StockDataService(db.session)
        watchlist_data = stock_service.get_user_watchlist(user_id)
        
        if not watchlist_data['watchlist']:
            return error_response("您还没有关注任何股票")
        
        # 批量分析
        service = get_analysis_service()
        results = []
        
        for item in watchlist_data['watchlist']:
            stock_code = item['stock']['code']
            try:
                result = service.run_analysis(stock_code, user_id)
                results.append({
                    'stock_code': stock_code,
                    'stock_name': item['stock']['name'],
                    'success': result['success'],
                    'error': result.get('error')
                })
            except Exception as e:
                results.append({
                    'stock_code': stock_code,
                    'stock_name': item['stock']['name'],
                    'success': False,
                    'error': str(e)
                })
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        return success_response(data={
            'results': results,
            'summary': {
                'total': total_count,
                'success': success_count,
                'failed': total_count - success_count
            }
        }, message=f"批量分析完成，成功 {success_count}/{total_count}")
        
    except Exception as e:
        logger.error(f"批量分析失败: {str(e)}")
        return error_response("批量分析失败", str(e))
