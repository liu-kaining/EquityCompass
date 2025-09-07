"""
分析相关API
"""
from flask import Blueprint, request, jsonify, session
from app.utils.response import success_response, error_response
from app.services.ai.analysis_service import AnalysisService
from app.services.data.usage_service import UsageTrackingService
from app import db
import logging
import json
import os

logger = logging.getLogger(__name__)

analysis_api_bp = Blueprint('analysis_api', __name__)

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_analysis_service():
    """获取分析服务实例"""
    return AnalysisService(db.session)

@analysis_api_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_stock():
    """分析股票（异步任务）"""
    try:
        # 检查用户登录状态
        user_id = session.get('user_id')
        is_admin = session.get('is_admin', False)
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        # 检查每日分析次数限制（管理员不受限制）
        if not is_admin:
            usage_service = UsageTrackingService(db.session)
            daily_limit = 10  # 每日最多10次分析
            limit_check = usage_service.check_daily_limit(user_id, daily_limit)
            
            if not limit_check['can_analyze']:
                return error_response(
                    f"今日分析次数已达上限（{daily_limit}次），请明天再试",
                    "DAILY_LIMIT_REACHED",
                    data={
                        'current_count': limit_check['current_count'],
                        'daily_limit': limit_check['daily_limit'],
                        'remaining': limit_check['remaining']
                    }
                )
        
        # 获取请求数据
        data = request.get_json()
        stock_code = data.get('stock_code', '').strip().upper()
        analysis_type = data.get('analysis_type', 'fundamental')  # fundamental, technical
        ai_provider = data.get('ai_provider', 'qwen')  # gemini, qwen, deepseek
        ai_model = data.get('ai_model')  # 新增：具体模型名称
        prompt_id = data.get('prompt_id')  # 新增：提示词ID
        
        if not stock_code:
            return error_response("INVALID_PARAM", "股票代码不能为空")
        
        # 创建分析服务
        service = get_analysis_service()
        
        # 创建单个分析任务
        task_id = service.create_single_analysis_task(
            user_id=user_id,
            stock_code=stock_code,
            analysis_type=analysis_type,
            ai_provider=ai_provider,
            ai_model=ai_model,
            prompt_id=prompt_id
        )
        
        # 立即增加使用次数（管理员不计入）
        if not is_admin:
            try:
                usage_service.increment_analysis_count(user_id)
            except Exception as e:
                logger.warning(f"增加使用次数失败: {str(e)}")
        
        return success_response(
            data={
                'task_id': task_id,
                'stock_code': stock_code,
                'analysis_type': analysis_type,
                'ai_provider': ai_provider
            },
            message=f"已提交 {stock_code} 的分析任务，请稍后查看结果"
        )
        
    except Exception as e:
        logger.error(f"提交分析任务失败: {str(e)}")
        return error_response("INTERNAL_ERROR", f"提交分析任务失败: {str(e)}")

@analysis_api_bp.route('/reports', methods=['GET'])
@login_required
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
        return error_response("INTERNAL_ERROR", f"获取报告失败: {str(e)}")

@analysis_api_bp.route('/reports/<stock_code>', methods=['GET'])
@login_required
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
            return error_response("NOT_FOUND", "报告不存在")
        
    except Exception as e:
        logger.error(f"获取股票报告失败: {str(e)}")
        return error_response("INTERNAL_ERROR", f"获取报告失败: {str(e)}")

@analysis_api_bp.route('/reports/<stock_code>/download', methods=['GET'])
@login_required
def download_stock_report(stock_code):
    """下载指定股票的分析报告"""
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
        
        if not report:
            return error_response("NOT_FOUND", "报告不存在")
        
        # 生成下载文件名
        filename = f"{stock_code}_{report['stock_name']}_分析报告_{report['analysis_date']}.txt"
        
        # 创建响应
        from flask import Response
        response = Response(
            report['content'],
            mimetype='text/plain; charset=utf-8',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        return response
        
    except Exception as e:
        logger.error(f"下载股票报告失败: {str(e)}")
        return error_response("INTERNAL_ERROR", f"下载报告失败: {str(e)}")

@analysis_api_bp.route('/reports/analysis-details/<int:report_id>', methods=['GET'])
@login_required
def get_analysis_details(report_id):
    """获取分析详情"""
    try:
        # 检查用户登录状态
        user_id = session.get('user_id')
        if not user_id:
            return error_response("请先登录", "UNAUTHORIZED")
        
        # 获取报告
        from app.models.analysis import ReportIndex
        report = ReportIndex.query.get(report_id)
        
        if not report:
            return error_response("NOT_FOUND", "报告不存在")
        
        # 检查权限：管理员可以查看所有报告，普通用户只能查看自己的报告
        is_admin = session.get('is_admin', False)
        if not is_admin:
            # 通过任务获取用户信息
            if report.generated_by_task_id:
                from app.models.analysis import AnalysisTask
                task = AnalysisTask.query.get(report.generated_by_task_id)
                if not task or task.user_id != user_id:
                    return error_response("PERMISSION_DENIED", "没有权限查看此报告")
            else:
                # 如果没有任务信息，暂时允许访问（可能是旧数据）
                pass
        
        # 获取分析详情
        service = get_analysis_service()
        details = service.get_analysis_details(report_id)
        
        if details:
            return success_response(data=details)
        else:
            return error_response("INTERNAL_ERROR", "无法获取分析详情")
        
    except Exception as e:
        logger.error(f"获取分析详情失败: {str(e)}")
        return error_response("INTERNAL_ERROR", f"获取分析详情失败: {str(e)}")

@analysis_api_bp.route('/batch-analyze', methods=['POST'])
@login_required
def batch_analyze():
    """批量分析API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据无效'}), 400
        
        stocks = data.get('stocks', [])
        analysis_type = data.get('analysis_type', 'fundamental')
        ai_provider = data.get('ai_provider', 'qwen')
        ai_model = data.get('ai_model')
        
        if not stocks:
            return jsonify({'success': False, 'message': '请选择要分析的股票'}), 400
        
        user_id = session.get('user_id')
        user_email = session.get('user_email', '')
        
        # 创建分析服务
        analysis_service = AnalysisService(db.session)
        
        # 创建批量分析任务
        task_id = analysis_service.create_batch_analysis_task(
            user_id=user_id,
            user_email=user_email,
            stocks=stocks,
            analysis_type=analysis_type,
            ai_provider=ai_provider,
            ai_model=ai_model
        )
        
        return jsonify({
            'success': True,
            'message': '批量分析任务已提交',
            'task_id': task_id,
            'stocks_count': len(stocks)
        })
        
    except Exception as e:
        logger.error(f"批量分析失败: {str(e)}")
        return jsonify({'success': False, 'message': f'批量分析失败: {str(e)}'}), 500

@analysis_api_bp.route('/task-status/<task_id>', methods=['GET'])
@login_required
def get_task_status(task_id):
    """获取任务状态"""
    try:
        user_id = session.get('user_id')
        is_admin = session.get('is_admin', False)
        analysis_service = AnalysisService(db.session)
        
        # 管理员可以查看所有任务，普通用户只能查看自己的任务
        if is_admin:
            # 管理员直接读取任务文件，不检查用户权限
            task_file = os.path.join(analysis_service.reports_dir, f"{task_id}.task.json")
            if not os.path.exists(task_file):
                return jsonify({'success': False, 'message': '任务不存在'}), 404
            
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
        else:
            # 普通用户使用原有的权限检查方法
            task_data = analysis_service.get_task_status(task_id, user_id)
            if not task_data:
                return jsonify({'success': False, 'message': '任务不存在或无权限访问'}), 404
        
        return jsonify({
            'success': True,
            'task': task_data
        })
        
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取任务状态失败: {str(e)}'}), 500

@analysis_api_bp.route('/tasks', methods=['GET'])
@login_required
def get_user_tasks():
    """获取用户的任务列表"""
    try:
        user_id = session.get('user_id')
        analysis_service = AnalysisService(db.session)
        
        tasks = analysis_service.get_user_tasks(user_id, limit=20)
        
        return jsonify({
            'success': True,
            'tasks': tasks
        })
        
    except Exception as e:
        logger.error(f"获取用户任务列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取任务列表失败: {str(e)}'}), 500

@analysis_api_bp.route('/retry-task/<task_id>', methods=['POST'])
@login_required
def retry_task(task_id):
    """手动重试任务"""
    try:
        user_id = session.get('user_id')
        analysis_service = AnalysisService(db.session)
        
        # 获取任务信息
        task_data = analysis_service.get_task_status(task_id, user_id)
        
        if not task_data:
            return jsonify({'success': False, 'message': '任务不存在或无权限访问'}), 404
        
        # 检查任务状态，只有失败的任务才能重试
        if task_data.get('status') != 'failed':
            return jsonify({'success': False, 'message': '只有失败的任务才能重试'}), 400
        
        # 重置任务状态
        task_data['status'] = 'pending'
        task_data['retry_count'] = 0
        task_data['retry_history'] = []
        task_data['failed_stocks'] = []
        task_data['completed_count'] = 0
        task_data['failed_count'] = 0
        task_data['started_at'] = None
        task_data['completed_at'] = None
        task_data['failed_at'] = None
        task_data['final_error'] = None
        
        # 保存更新后的任务数据
        task_file = os.path.join(analysis_service.reports_dir, f"{task_id}.task.json")
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
        
        # 重新启动任务
        if task_data.get('task_id', '').startswith('single_'):
            # 单个分析任务
            analysis_service._retry_single_task(task_data)
        else:
            # 批量分析任务
            analysis_service._retry_batch_task(task_data)
        
        return jsonify({
            'success': True,
            'message': '任务重试已启动'
        })
        
    except Exception as e:
        logger.error(f"重试任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'重试任务失败: {str(e)}'}), 500

@analysis_api_bp.route('/usage', methods=['GET'])
@login_required
def get_user_usage():
    """获取用户今日使用量"""
    try:
        user_id = session.get('user_id')
        is_admin = session.get('is_admin', False)
        
        if is_admin:
            # 管理员不受限制
            return jsonify({
                'success': True,
                'usage': {
                    'user_id': user_id,
                    'current_count': 0,
                    'daily_limit': 999,  # 无限制
                    'remaining': 999,
                    'can_analyze': True,
                    'is_limit_reached': False,
                    'is_admin': True
                }
            })
        
        usage_service = UsageTrackingService(db.session)
        daily_limit = 10
        usage_data = usage_service.check_daily_limit(user_id, daily_limit)
        usage_data['is_admin'] = False
        
        return jsonify({
            'success': True,
            'usage': usage_data
        })
        
    except Exception as e:
        logger.error(f"获取用户使用量失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取使用量失败: {str(e)}'}), 500

@analysis_api_bp.route('/task-pause/<task_id>', methods=['POST'])
@login_required
def pause_task(task_id):
    """强制暂停任务"""
    try:
        user_id = session.get('user_id')
        analysis_service = AnalysisService(db.session)
        
        # 获取任务信息
        task_data = analysis_service.get_task_status(task_id, user_id)
        
        if not task_data:
            return error_response('任务不存在或无权限访问', 'NOT_FOUND')
        
        # 检查任务状态，只有进行中的任务才能暂停
        if task_data.get('status') not in ['pending', 'running']:
            return error_response('只有等待中或进行中的任务才能暂停', 'INVALID_STATUS')
        
        # 暂停任务
        success = analysis_service.pause_task(task_id, user_id)
        
        if success:
            return success_response(message='任务已暂停')
        else:
            return error_response('OPERATION_FAILED', '暂停任务失败')
        
    except Exception as e:
        logger.error(f"暂停任务失败: {str(e)}")
        return error_response('INTERNAL_ERROR', f'暂停任务失败: {str(e)}')

@analysis_api_bp.route('/task-resume/<task_id>', methods=['POST'])
@login_required
def resume_task(task_id):
    """恢复任务"""
    try:
        user_id = session.get('user_id')
        analysis_service = AnalysisService(db.session)
        
        # 获取任务信息
        task_data = analysis_service.get_task_status(task_id, user_id)
        
        if not task_data:
            return error_response('NOT_FOUND', '任务不存在')
        
        # 检查任务状态，只有暂停的任务才能恢复
        if task_data.get('status') != 'paused':
            return error_response('只有暂停的任务才能恢复', 'INVALID_STATUS')
        
        # 恢复任务
        success = analysis_service.resume_task(task_id, user_id)
        
        if success:
            return success_response(message='任务已恢复')
        else:
            return error_response('OPERATION_FAILED', '恢复任务失败')
        
    except Exception as e:
        logger.error(f"恢复任务失败: {str(e)}")
        return error_response('INTERNAL_ERROR', f'恢复任务失败: {str(e)}')

@analysis_api_bp.route('/task-delete/<task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """删除任务"""
    try:
        user_id = session.get('user_id')
        analysis_service = AnalysisService(db.session)
        
        # 获取任务信息
        task_data = analysis_service.get_task_status(task_id, user_id)
        
        if not task_data:
            return error_response('NOT_FOUND', '任务不存在或无权限访问')
        
        # 检查任务状态，只有已完成或失败的任务才能删除
        if task_data.get('status') in ['pending', 'running']:
            return error_response('INVALID_STATUS', '进行中的任务无法删除，请先暂停任务')
        
        # 删除任务
        success = analysis_service.delete_task(task_id, user_id)
        
        if success:
            return success_response(message='任务已删除')
        else:
            return error_response('OPERATION_FAILED', '删除任务失败')
        
    except Exception as e:
        logger.error(f"删除任务失败: {str(e)}")
        return error_response('INTERNAL_ERROR', f'删除任务失败: {str(e)}')
