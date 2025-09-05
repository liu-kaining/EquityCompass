"""
AI分析服务 - 简化版本
使用文件存储替代Redis
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.repositories.stock_repository import StockRepository
from app.repositories.watchlist_repository import WatchlistRepository

logger = logging.getLogger(__name__)


class AnalysisService:
    """AI分析服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.stock_repo = StockRepository(session)
        self.watchlist_repo = WatchlistRepository(session)
        self.reports_dir = 'data/reports'
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保目录存在"""
        os.makedirs('data', exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def _get_analysis_prompt(self, prompt_type: str = 'default') -> str:
        """获取分析提示词模板"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
            from prompts import PROMPT_CONFIG
            
            if prompt_type == 'fundamental':
                return PROMPT_CONFIG['fundamental']
            elif prompt_type == 'technical':
                return PROMPT_CONFIG['technical']
            else:
                # 默认使用基本面分析
                return PROMPT_CONFIG['fundamental']
                
        except ImportError:
            # 如果无法导入配置，返回错误
            raise Exception("无法导入提示词配置，请检查 prompts.py 文件")
    
    def create_analysis_task(self, stock_code: str, user_id: int) -> str:
        """创建分析任务"""
        task_id = f"{stock_code}_{user_id}_{int(datetime.utcnow().timestamp())}"
        logger.info(f"创建分析任务: {task_id}")
        return task_id
    
    def run_analysis(self, stock_code: str, user_id: int, analysis_type: str = 'fundamental', ai_provider: str = 'qwen') -> Dict[str, Any]:
        """运行分析（同步版本）"""
        try:
            # 获取股票信息
            stock = self.stock_repo.get_by_code(stock_code)
            if not stock:
                raise Exception(f"股票不存在: {stock_code}")
            
            # 生成分析报告
            report_data = self._generate_analysis_report(stock, analysis_type, ai_provider)
            
            # 检查分析是否成功
            if not report_data.get('success', True):  # 默认True是为了兼容旧代码
                return {
                    'success': False,
                    'error': report_data.get('error', '分析失败')
                }
            
            # 保存报告
            self.save_analysis_report(stock_code, report_data)
            
            return {
                'success': True,
                'task_id': f"{stock_code}_{user_id}_{int(datetime.utcnow().timestamp())}",
                'report': report_data
            }
            
        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _run_analysis_with_retry(self, stock_code: str, user_id: int, analysis_type: str, 
                                ai_provider: str, task_data: Dict, task_file: str) -> Dict[str, Any]:
        """带重试机制的分析执行"""
        import time
        
        max_retries = task_data.get('max_retries', 5)
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                logger.info(f"尝试分析 {stock_code} (第 {retry_count + 1} 次)")
                
                # 执行分析
                result = self.run_analysis(stock_code, user_id, analysis_type, ai_provider)
                
                if result['success']:
                    logger.info(f"股票 {stock_code} 分析成功")
                    return result
                else:
                    # 分析失败，记录错误
                    error_msg = result.get('error', '未知错误')
                    logger.warning(f"股票 {stock_code} 分析失败 (第 {retry_count + 1} 次): {error_msg}")
                    
                    # 记录重试历史
                    retry_record = {
                        'attempt': retry_count + 1,
                        'timestamp': datetime.utcnow().isoformat(),
                        'error': error_msg
                    }
                    task_data['retry_history'].append(retry_record)
                    task_data['retry_count'] = retry_count + 1
                    
                    # 更新任务文件
                    with open(task_file, 'w', encoding='utf-8') as f:
                        json.dump(task_data, f, ensure_ascii=False, indent=2)
                    
                    # 如果还有重试机会，等待后重试
                    if retry_count < max_retries:
                        wait_time = min(30, (retry_count + 1) * 10)  # 递增等待时间，最多30秒
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        retry_count += 1
                    else:
                        # 重试次数用完，返回失败
                        logger.error(f"股票 {stock_code} 分析失败，已重试 {max_retries} 次")
                        return {
                            'success': False,
                            'error': f"分析失败，已重试 {max_retries} 次。最后一次错误: {error_msg}"
                        }
                        
            except Exception as e:
                error_msg = str(e)
                logger.error(f"股票 {stock_code} 分析异常 (第 {retry_count + 1} 次): {error_msg}")
                
                # 记录重试历史
                retry_record = {
                    'attempt': retry_count + 1,
                    'timestamp': datetime.utcnow().isoformat(),
                    'error': error_msg
                }
                task_data['retry_history'].append(retry_record)
                task_data['retry_count'] = retry_count + 1
                
                # 更新任务文件
                with open(task_file, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)
                
                # 如果还有重试机会，等待后重试
                if retry_count < max_retries:
                    wait_time = min(30, (retry_count + 1) * 10)  # 递增等待时间，最多30秒
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    retry_count += 1
                else:
                    # 重试次数用完，返回失败
                    logger.error(f"股票 {stock_code} 分析异常，已重试 {max_retries} 次")
                    return {
                        'success': False,
                        'error': f"分析异常，已重试 {max_retries} 次。最后一次错误: {error_msg}"
                    }
        
        # 理论上不会到达这里
        return {
            'success': False,
            'error': '重试机制异常'
        }
    
    def _run_analysis_with_retry_for_batch(self, stock_code: str, user_id: int, analysis_type: str, 
                                         ai_provider: str, task_data: Dict, task_file: str) -> Dict[str, Any]:
        """批量分析中的单个股票重试机制"""
        import time
        
        max_retries = task_data.get('max_retries', 5)
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                logger.info(f"尝试分析 {stock_code} (第 {retry_count + 1} 次)")
                
                # 执行分析
                result = self.run_analysis(stock_code, user_id, analysis_type, ai_provider)
                
                if result['success']:
                    logger.info(f"股票 {stock_code} 分析成功")
                    return result
                else:
                    # 分析失败，记录错误
                    error_msg = result.get('error', '未知错误')
                    logger.warning(f"股票 {stock_code} 分析失败 (第 {retry_count + 1} 次): {error_msg}")
                    
                    # 如果还有重试机会，等待后重试
                    if retry_count < max_retries:
                        wait_time = min(30, (retry_count + 1) * 10)  # 递增等待时间，最多30秒
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        retry_count += 1
                    else:
                        # 重试次数用完，返回失败
                        logger.error(f"股票 {stock_code} 分析失败，已重试 {max_retries} 次")
                        return {
                            'success': False,
                            'error': f"分析失败，已重试 {max_retries} 次。最后一次错误: {error_msg}",
                            'retry_count': retry_count
                        }
                        
            except Exception as e:
                error_msg = str(e)
                logger.error(f"股票 {stock_code} 分析异常 (第 {retry_count + 1} 次): {error_msg}")
                
                # 如果还有重试机会，等待后重试
                if retry_count < max_retries:
                    wait_time = min(30, (retry_count + 1) * 10)  # 递增等待时间，最多30秒
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    retry_count += 1
                else:
                    # 重试次数用完，返回失败
                    logger.error(f"股票 {stock_code} 分析异常，已重试 {max_retries} 次")
                    return {
                        'success': False,
                        'error': f"分析异常，已重试 {max_retries} 次。最后一次错误: {error_msg}",
                        'retry_count': retry_count
                    }
        
        # 理论上不会到达这里
        return {
            'success': False,
            'error': '重试机制异常',
            'retry_count': 0
        }
    
    def _generate_analysis_report(self, stock, analysis_type: str = 'fundamental', ai_provider: str = 'qwen') -> Dict[str, Any]:
        """生成分析报告"""
        try:
            from app.services.ai.llm_provider import LLMProviderFactory
            from flask import current_app
            
            logger.info(f"开始生成分析报告 - 股票: {stock.code}, 分析类型: {analysis_type}, AI提供商: {ai_provider}")
            
            # 根据指定的AI提供商获取配置
            if ai_provider == 'gemini':
                provider_config = {
                    'name': 'gemini',
                    'api_key': os.getenv('GEMINI_API_KEY'),
                    'model': os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'),
                    'max_tokens': 15000,  # 大幅增加token限制，确保生成详细报告
                    'temperature': 0.7
                }
                logger.info(f"Gemini配置: 模型={provider_config['model']}, max_tokens={provider_config['max_tokens']}")
            elif ai_provider == 'qwen':
                provider_config = {
                    'name': 'qwen',
                    'api_key': os.getenv('QWEN_API_KEY'),
                    'model': os.getenv('QWEN_MODEL', 'qwen-deep-research'),
                    'max_tokens': 15000,  # 大幅增加token限制，确保生成详细报告
                    'temperature': 0.7,
                    'enable_deep_thinking': True,  # 启用深度思考
                    'enable_web_search': True,  # 启用全网搜索
                    'thinking_steps': int(os.getenv('QWEN_THINKING_STEPS', '3'))  # 思考步数
                }
                logger.info(f"Qwen配置: 模型={provider_config['model']}, max_tokens={provider_config['max_tokens']}, 深度思考={provider_config['enable_deep_thinking']}, 全网搜索={provider_config['enable_web_search']}, 思考步数={provider_config['thinking_steps']}")
            elif ai_provider == 'deepseek':
                provider_config = {
                    'name': 'deepseek',
                    'api_key': os.getenv('DEEPSEEK_API_KEY'),
                    'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner'),
                    'max_tokens': 15000,  # 大幅增加token限制，确保生成详细报告
                    'temperature': 0.7,
                    'enable_deep_thinking': True,  # 重新启用深度思考
                    'thinking_steps': int(os.getenv('DEEPSEEK_THINKING_STEPS', '3'))  # 思考步数
                }
                logger.info(f"DeepSeek配置: 模型={provider_config['model']}, max_tokens={provider_config['max_tokens']}, 深度思考={provider_config['enable_deep_thinking']}, 思考步数={provider_config['thinking_steps']}")
            else:
                # 默认使用Qwen
                provider_config = {
                    'name': 'qwen',
                    'api_key': os.getenv('QWEN_API_KEY'),
                    'model': os.getenv('QWEN_MODEL', 'qwen-deep-research'),
                    'max_tokens': 15000,  # 大幅增加token限制，确保生成详细报告
                    'temperature': 0.7,
                    'enable_deep_thinking': True,  # 启用深度思考
                    'enable_web_search': True,  # 启用全网搜索
                    'thinking_steps': int(os.getenv('QWEN_THINKING_STEPS', '3'))  # 思考步数
                }
                logger.info(f"默认Qwen配置: 模型={provider_config['model']}, max_tokens={provider_config['max_tokens']}, 深度思考={provider_config['enable_deep_thinking']}, 全网搜索={provider_config['enable_web_search']}, 思考步数={provider_config['thinking_steps']}")
            
            # 如果没有API密钥，返回模拟数据
            if not provider_config['api_key']:
                logger.warning(f"{ai_provider} API密钥未配置，返回demo内容")
                return {
                    'stock_code': stock.code,
                    'stock_name': stock.name,
                    'market': stock.market,
                    'analysis_date': datetime.utcnow().strftime('%Y-%m-%d'),
                    'content': f"# {stock.name} ({stock.code}) 分析报告\n\n## 技术面分析\n\n## 基本面分析\n\n## 投资建议\n\n## 市场展望",
                    'provider': 'demo',
                    'analysis_type': analysis_type,
                    'metadata': {
                        'timestamp': datetime.utcnow().isoformat(),
                        'note': f'请配置{ai_provider.upper()}_API_KEY环境变量以使用真实AI分析'
                    }
                }
            
            # 创建Provider
            logger.info(f"创建{ai_provider} Provider...")
            provider = LLMProviderFactory.create_provider(ai_provider, provider_config)
            
            # 准备股票信息
            stock_info = {
                'code': stock.code,
                'name': stock.name,
                'market': stock.market,
                'industry': stock.industry or '未知',
                'exchange': stock.exchange or '未知',
                'analysis_date': datetime.utcnow().strftime('%Y-%m-%d')
            }
            logger.info(f"股票信息: {stock_info}")
            
            # 生成分析报告
            prompt_template = self._get_analysis_prompt(analysis_type)
            logger.info(f"获取到提示词模板，长度: {len(prompt_template)} 字符")
            logger.info(f"开始调用{ai_provider}生成分析...")
            result = provider.generate_analysis(prompt_template, stock_info)
            
            if result['success']:
                logger.info(f"AI分析成功 - 股票: {stock.code}, 提供商: {ai_provider}, 内容长度: {len(result['content'])} 字符")
                logger.info(f"分析结果元数据: {result.get('metadata', {})}")
                
                return {
                    'stock_code': stock.code,
                    'stock_name': stock.name,
                    'market': stock.market,
                    'analysis_date': stock_info['analysis_date'],
                    'content': result['content'],
                    'provider': ai_provider,
                    'analysis_type': analysis_type,
                    'metadata': {
                        'tokens_used': result.get('tokens_used'),
                        'response_time': result.get('response_time'),
                        'model': result.get('model'),
                        'timestamp': result.get('timestamp')
                    }
                }
            else:
                # 如果AI分析失败，不生成报告，直接返回失败状态
                logger.error(f"AI分析失败 - 股票: {stock.code}, 提供商: {ai_provider}, 错误: {result.get('error', '未知错误')}")
                return {
                    'success': False,
                    'error': result.get('error', '未知错误'),
                    'stock_code': stock.code,
                    'stock_name': stock.name,
                    'market': stock.market,
                    'analysis_date': datetime.utcnow().strftime('%Y-%m-%d'),
                    'provider': ai_provider,
                    'analysis_type': analysis_type,
                    'metadata': {
                        'error': result.get('error'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"生成分析报告失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'stock_code': stock.code,
                'stock_name': stock.name,
                'market': stock.market,
                'analysis_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'provider': 'error',
                'analysis_type': analysis_type,
                'metadata': {
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
    
    def save_analysis_report(self, stock_code: str, report_data: Dict[str, Any]) -> str:
        """保存分析报告到文件并注册到数据库"""
        try:
            # 创建日期目录
            date_str = datetime.utcnow().strftime('%Y-%m-%d')
            date_dir = os.path.join(self.reports_dir, date_str)
            os.makedirs(date_dir, exist_ok=True)
            
            # 生成唯一的时间戳，确保每次分析都是新文件
            timestamp = datetime.utcnow().strftime('%H%M%S_%f')[:-3]  # 精确到毫秒
            ai_provider = report_data.get('provider', 'unknown')
            analysis_type = report_data.get('analysis_type', 'fundamental')
            
            # 文件名格式：股票代码_时间戳_模型_分析类型.json
            filename = f"{stock_code}_{timestamp}_{ai_provider}_{analysis_type}.json"
            report_file = os.path.join(date_dir, filename)
            
            # 添加元数据
            report_data['report_id'] = f"{stock_code}_{timestamp}"
            report_data['created_at'] = datetime.utcnow().isoformat()
            report_data['analysis_type'] = analysis_type
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            # 注册到数据库
            self._register_report_to_database(stock_code, report_data, report_file)
            
            logger.info(f"保存分析报告: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"保存分析报告失败: {str(e)}")
            raise
    
    def _register_report_to_database(self, stock_code: str, report_data: Dict[str, Any], report_file: str):
        """将报告注册到数据库"""
        try:
            from app.models.analysis import ReportIndex
            from app.models.stock import Stock
            from app import db
            
            # 获取股票信息
            stock = Stock.query.filter_by(code=stock_code).first()
            if not stock:
                logger.error(f"未找到股票: {stock_code}")
                return
            
            # 允许同一股票同一天有多个报告，不再检查重复
            
            # 创建新的报告索引记录
            # 处理analysis_date，确保是date对象
            analysis_date_str = report_data.get('analysis_date', datetime.utcnow().strftime('%Y-%m-%d'))
            if isinstance(analysis_date_str, str):
                from datetime import date
                analysis_date = datetime.strptime(analysis_date_str, '%Y-%m-%d').date()
            else:
                analysis_date = analysis_date_str
            
            report_index = ReportIndex(
                stock_id=stock.id,
                analysis_date=analysis_date,
                file_path=report_file,
                summary=report_data.get('content', '')[:500] if report_data.get('content') else '',  # 截取前500字符作为摘要
                generated_at=datetime.utcnow()
            )
            
            db.session.add(report_index)
            db.session.commit()
            
            logger.info(f"成功注册报告到数据库: {stock_code} - {report_data.get('analysis_date')}")
            
        except Exception as e:
            logger.error(f"注册报告到数据库失败: {str(e)}")
            # 不抛出异常，避免影响报告保存
    
    def get_analysis_report(self, stock_code: str, date: str = None, report_id: str = None) -> Optional[Dict[str, Any]]:
        """获取分析报告"""
        try:
            if not date:
                date = datetime.utcnow().strftime('%Y-%m-%d')
            
            logger.info(f"获取分析报告 - 股票代码: {stock_code}, 日期: {date}, 报告ID: {report_id}")
            
            if report_id:
                # 如果指定了report_id，需要解析report_id来找到对应的文件
                # report_id格式: stock_code_timestamp
                logger.info(f"使用report_id查找报告: {report_id}")
                
                # 遍历所有日期目录，查找包含该report_id的文件
                if os.path.exists(self.reports_dir):
                    for date_dir in sorted(os.listdir(self.reports_dir), reverse=True):
                        date_path = os.path.join(self.reports_dir, date_dir)
                        if not os.path.isdir(date_path):
                            continue
                        
                        for filename in os.listdir(date_path):
                            if filename.endswith('.json'):
                                report_file = os.path.join(date_path, filename)
                                try:
                                    with open(report_file, 'r', encoding='utf-8') as f:
                                        report_data = json.load(f)
                                        # 检查文件中的report_id是否匹配
                                        if report_data.get('report_id') == report_id:
                                            logger.info(f"找到报告文件: {report_file}")
                                            logger.info(f"成功读取报告文件: {report_file}")
                                            return report_data
                                except Exception as e:
                                    logger.error(f"读取报告文件失败: {report_file}, {str(e)}")
                
                logger.warning(f"未找到report_id为 {report_id} 的报告")
                return None
            else:
                # 否则查找该股票最新的报告
                date_dir = os.path.join(self.reports_dir, date)
                if os.path.exists(date_dir):
                    # 查找该股票的所有报告文件
                    stock_reports = []
                    for filename in os.listdir(date_dir):
                        if filename.startswith(f"{stock_code}_") and filename.endswith('.json'):
                            report_file = os.path.join(date_dir, filename)
                            try:
                                with open(report_file, 'r', encoding='utf-8') as f:
                                    report_data = json.load(f)
                                    stock_reports.append((report_data.get('created_at', ''), report_data))
                            except Exception as e:
                                logger.error(f"读取报告文件失败: {report_file}, {str(e)}")
                    
                    # 返回最新的报告
                    if stock_reports:
                        stock_reports.sort(key=lambda x: x[0], reverse=True)
                        logger.info(f"返回最新报告: {stock_reports[0][1].get('report_id', 'unknown')}")
                        return stock_reports[0][1]
            
            logger.warning(f"未找到股票 {stock_code} 的报告")
            return None
                
        except Exception as e:
            logger.error(f"获取分析报告失败: {str(e)}")
            return None
    
    def get_all_reports_for_stock(self, stock_code: str) -> List[Dict[str, Any]]:
        """获取指定股票的所有分析报告"""
        try:
            reports = []
            
            # 遍历所有日期目录，查找该股票的所有报告
            if os.path.exists(self.reports_dir):
                for date_dir in sorted(os.listdir(self.reports_dir), reverse=True):
                    date_path = os.path.join(self.reports_dir, date_dir)
                    if not os.path.isdir(date_path):
                        continue
                    
                    for filename in os.listdir(date_path):
                        if filename.startswith(f"{stock_code}_") and filename.endswith('.json'):
                            report_file = os.path.join(date_path, filename)
                            try:
                                with open(report_file, 'r', encoding='utf-8') as f:
                                    report_data = json.load(f)
                                    report_data['date'] = date_dir
                                    reports.append(report_data)
                            except Exception as e:
                                logger.error(f"读取报告文件失败: {report_file}, {str(e)}")
            
            # 按创建时间倒序排列
            reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            logger.info(f"找到股票 {stock_code} 的 {len(reports)} 个报告")
            return reports
                
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 的所有报告失败: {str(e)}")
            return []
    
    def get_user_reports(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户的分析报告"""
        try:
            reports = []
            
            # 获取用户关注的股票
            user_stocks = self.watchlist_repo.get_user_stock_codes(user_id)
            
            # 遍历报告目录，获取所有报告
            if os.path.exists(self.reports_dir):
                for date_dir in sorted(os.listdir(self.reports_dir), reverse=True):
                    date_path = os.path.join(self.reports_dir, date_dir)
                    if not os.path.isdir(date_path):
                        continue
                    
                    for file_name in os.listdir(date_path):
                        if file_name.endswith('.json'):
                            # 解析文件名：股票代码_时间戳_毫秒数_模型_分析类型.json 或 股票代码_描述_序号.json
                            parts = file_name.replace('.json', '').split('_')
                            if len(parts) >= 5:
                                # 标准格式：股票代码_时间戳_毫秒数_模型_分析类型.json
                                stock_code = parts[0]
                                timestamp = f"{parts[1]}_{parts[2]}"  # 重新组合时间戳
                                ai_provider = parts[3]
                                analysis_type = parts[4]
                            elif len(parts) >= 3:
                                # 简化格式：股票代码_描述_序号.json
                                stock_code = parts[0]
                                timestamp = parts[1] if len(parts) > 1 else 'test'
                                ai_provider = 'qwen-deep-research'  # 默认模型
                                analysis_type = 'comprehensive'  # 默认分析类型
                            else:
                                # 跳过格式不正确的文件
                                continue
                                
                            report_file = os.path.join(date_path, file_name)
                            try:
                                with open(report_file, 'r', encoding='utf-8') as f:
                                    report_data = json.load(f)
                                    report_data['date'] = date_dir
                                    report_data['stock_code'] = stock_code
                                    report_data['ai_provider'] = ai_provider
                                    report_data['analysis_type'] = analysis_type
                                    report_data['timestamp'] = timestamp
                                    # 标记是否为用户关注的股票
                                    report_data['is_watched'] = stock_code in user_stocks
                                    reports.append(report_data)
                            except Exception as e:
                                logger.error(f"读取报告文件失败: {report_file}, {str(e)}")
                    
                    if len(reports) >= limit:
                        break
            
            # 按创建时间排序，最新的在前
            reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return reports[:limit]
            
        except Exception as e:
            logger.error(f"获取用户报告失败: {str(e)}")
            return []

    def get_all_reports(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取所有分析报告（不需要登录）"""
        try:
            reports = []
            
            # 遍历报告目录，获取所有报告
            if os.path.exists(self.reports_dir):
                for date_dir in sorted(os.listdir(self.reports_dir), reverse=True):
                    date_path = os.path.join(self.reports_dir, date_dir)
                    if not os.path.isdir(date_path):
                        continue
                    
                    for file_name in os.listdir(date_path):
                        if file_name.endswith('.json'):
                            # 解析文件名：股票代码_时间戳_毫秒数_模型_分析类型.json 或 股票代码_描述_序号.json
                            parts = file_name.replace('.json', '').split('_')
                            if len(parts) >= 5:
                                # 标准格式：股票代码_时间戳_毫秒数_模型_分析类型.json
                                stock_code = parts[0]
                                timestamp = f"{parts[1]}_{parts[2]}"  # 重新组合时间戳
                                ai_provider = parts[3]
                                analysis_type = parts[4]
                            elif len(parts) >= 3:
                                # 简化格式：股票代码_描述_序号.json
                                stock_code = parts[0]
                                timestamp = parts[1] if len(parts) > 1 else 'test'
                                ai_provider = 'qwen-deep-research'  # 默认模型
                                analysis_type = 'comprehensive'  # 默认分析类型
                            else:
                                # 跳过格式不正确的文件
                                continue
                                
                            report_file = os.path.join(date_path, file_name)
                            try:
                                with open(report_file, 'r', encoding='utf-8') as f:
                                    report_data = json.load(f)
                                    report_data['date'] = date_dir
                                    report_data['stock_code'] = stock_code
                                    report_data['ai_provider'] = ai_provider
                                    report_data['analysis_type'] = analysis_type
                                    report_data['timestamp'] = timestamp
                                    # 未登录用户，不标记关注状态
                                    report_data['is_watched'] = False
                                    reports.append(report_data)
                            except Exception as e:
                                logger.error(f"读取报告文件失败: {report_file}, {str(e)}")
                    
                    if len(reports) >= limit:
                        break
            
            # 按创建时间排序，最新的在前
            reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return reports[:limit]
            
        except Exception as e:
            logger.error(f"获取所有报告失败: {str(e)}")
            return []

    def get_global_reports_count(self) -> int:
        """获取全局报告总数（管理员功能）"""
        try:
            total_count = 0
            if os.path.exists(self.reports_dir):
                for date_dir in os.listdir(self.reports_dir):
                    date_path = os.path.join(self.reports_dir, date_dir)
                    if os.path.isdir(date_path):
                        json_files = [f for f in os.listdir(date_path) if f.endswith('.json')]
                        total_count += len(json_files)
            return total_count
        except Exception as e:
            logger.error(f"获取全局报告数量失败: {str(e)}")
            return 0

    def get_user_accessible_reports_count(self, user_id: int) -> int:
        """获取用户可访问的报告数量（基于关注列表）"""
        try:
            # 获取用户关注的股票
            user_stocks = self.watchlist_repo.get_user_stock_codes(user_id)
            
            accessible_count = 0
            if os.path.exists(self.reports_dir):
                for date_dir in os.listdir(self.reports_dir):
                    date_path = os.path.join(self.reports_dir, date_dir)
                    if os.path.isdir(date_path):
                        for file_name in os.listdir(date_path):
                            if file_name.endswith('.json'):
                                stock_code = file_name.replace('.json', '')
                                if stock_code in user_stocks:
                                    accessible_count += 1
            return accessible_count
        except Exception as e:
            logger.error(f"获取用户可访问报告数量失败: {str(e)}")
            return 0

    def create_single_analysis_task(self, user_id: int, stock_code: str, 
                                  analysis_type: str = 'fundamental', ai_provider: str = 'gemini') -> str:
        """创建单个分析任务"""
        try:
            import threading
            import time
            from app.services.ai.task_manager import task_manager
            
            # 生成任务ID
            task_id = f"single_{stock_code}_{user_id}_{int(time.time())}"
            
            # 创建任务记录
            task_data = {
                'task_id': task_id,
                'user_id': user_id,
                'stock_code': stock_code,
                'analysis_type': analysis_type,
                'ai_provider': ai_provider,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'total_count': 1,
                'completed_count': 0,
                'failed_count': 0,
                'retry_count': 0,
                'max_retries': 5,
                'retry_history': []
            }
            
            # 保存任务信息到文件
            task_file = os.path.join(self.reports_dir, f"{task_id}.task.json")
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            
            # 在后台线程中执行单个分析
            def run_single_analysis():
                try:
                    # 创建Flask应用上下文
                    from app import create_app
                    app = create_app()
                    
                    with app.app_context():
                        logger.info(f"开始执行单个分析任务: {task_id}")
                        
                        # 更新任务状态为进行中
                        task_data['status'] = 'running'
                        task_data['started_at'] = datetime.utcnow().isoformat()
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
                        
                        # 检查是否被暂停或停止
                        if not task_manager.wait_if_paused(task_id):
                            logger.info(f"任务 {task_id} 被停止，退出执行")
                            task_data['status'] = 'stopped'
                            task_data['stopped_at'] = datetime.utcnow().isoformat()
                            with open(task_file, 'w', encoding='utf-8') as f:
                                json.dump(task_data, f, ensure_ascii=False, indent=2)
                            
                            # 从任务管理器中注销被停止的任务
                            task_manager.unregister_task(task_id)
                            return
                        
                        # 执行分析（带重试机制）
                        result = self._run_analysis_with_retry(stock_code, user_id, analysis_type, ai_provider, task_data, task_file)
                        
                        if result['success']:
                            task_data['completed_count'] = 1
                            task_data['status'] = 'completed'
                            task_data['progress'] = 100
                            logger.info(f"股票 {stock_code} 分析成功")
                        else:
                            task_data['failed_count'] = 1
                            task_data['status'] = 'failed'
                            task_data['error'] = result.get('error', '分析失败')
                            task_data['final_error'] = result.get('error', '分析失败')
                            logger.error(f"股票 {stock_code} 分析失败: {result.get('error')}")
                        
                        # 更新任务状态
                        task_data['completed_at'] = datetime.utcnow().isoformat()
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
                        
                        # 从任务管理器中注销已完成的任务
                        task_manager.unregister_task(task_id)
                        
                        logger.info(f"单个分析任务完成: {task_id}")
                    
                except Exception as e:
                    logger.error(f"单个分析任务执行失败: {task_id}, 错误: {str(e)}")
                    task_data['status'] = 'failed'
                    task_data['error'] = str(e)
                    task_data['final_error'] = str(e)
                    task_data['failed_at'] = datetime.utcnow().isoformat()
                    with open(task_file, 'w', encoding='utf-8') as f:
                        json.dump(task_data, f, ensure_ascii=False, indent=2)
                    
                    # 从任务管理器中注销失败的任务
                    task_manager.unregister_task(task_id)
            
            # 启动后台线程
            analysis_thread = threading.Thread(target=run_single_analysis)
            analysis_thread.daemon = True
            analysis_thread.start()
            
            # 注册到任务管理器
            task_manager.register_task(task_id, analysis_thread, 'single_analysis')
            
            logger.info(f"单个分析任务已创建: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"创建单个分析任务失败: {str(e)}")
            raise e

    def create_batch_analysis_task(self, user_id: int, user_email: str, stocks: List[Dict], 
                                  analysis_type: str = 'fundamental', ai_provider: str = 'qwen') -> str:
        """创建批量分析任务"""
        try:
            import threading
            import time
            from app.services.ai.task_manager import task_manager
            
            # 生成任务ID
            task_id = f"batch_{user_id}_{int(time.time())}"
            
            # 创建任务记录
            task_data = {
                'task_id': task_id,
                'user_id': user_id,
                'user_email': user_email,
                'stocks': stocks,
                'analysis_type': analysis_type,
                'ai_provider': ai_provider,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'total_count': len(stocks),
                'completed_count': 0,
                'failed_count': 0,
                'max_retries': 5,
                'failed_stocks': [],
                'stock_status': {}  # 记录每个股票的状态
            }
            
            # 保存任务信息到文件
            task_file = os.path.join(self.reports_dir, f"{task_id}.task.json")
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            
            # 在后台线程中执行批量分析
            def run_batch_analysis():
                try:
                    # 创建Flask应用上下文
                    from app import create_app
                    app = create_app()
                    
                    with app.app_context():
                        logger.info(f"开始执行批量分析任务: {task_id}")
                        
                        # 更新任务状态为进行中
                        task_data['status'] = 'running'
                        task_data['started_at'] = datetime.utcnow().isoformat()
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
                        
                        # 逐个分析股票
                        for i, stock in enumerate(stocks):
                            try:
                                # 检查是否被暂停或停止
                                if not task_manager.wait_if_paused(task_id):
                                    logger.info(f"任务 {task_id} 被停止，退出执行")
                                    task_data['status'] = 'stopped'
                                    task_data['stopped_at'] = datetime.utcnow().isoformat()
                                    with open(task_file, 'w', encoding='utf-8') as f:
                                        json.dump(task_data, f, ensure_ascii=False, indent=2)
                                    
                                    # 从任务管理器中注销被停止的任务
                                    task_manager.unregister_task(task_id)
                                    return
                                
                                stock_code = stock['code']
                                logger.info(f"分析股票 {i+1}/{len(stocks)}: {stock_code}")
                                
                                # 执行分析（带重试机制）
                                result = self._run_analysis_with_retry_for_batch(stock_code, user_id, analysis_type, ai_provider, task_data, task_file)
                                
                                if result['success']:
                                    task_data['completed_count'] += 1
                                    task_data['stock_status'][stock_code] = {
                                        'status': 'completed',
                                        'retry_count': result.get('retry_count', 0),
                                        'completed_at': datetime.utcnow().isoformat()
                                    }
                                    logger.info(f"股票 {stock_code} 分析成功")
                                else:
                                    task_data['failed_count'] += 1
                                    # 记录失败的股票信息
                                    failed_stock_info = {
                                        'code': stock_code,
                                        'name': stock.get('name', ''),
                                        'error': result.get('error', '分析失败'),
                                        'retry_count': result.get('retry_count', 0)
                                    }
                                    task_data['failed_stocks'].append(failed_stock_info)
                                    task_data['stock_status'][stock_code] = {
                                        'status': 'failed',
                                        'retry_count': result.get('retry_count', 0),
                                        'error': result.get('error', '分析失败'),
                                        'failed_at': datetime.utcnow().isoformat()
                                    }
                                    logger.error(f"股票 {stock_code} 分析失败: {result.get('error')}")
                                
                                # 更新进度
                                task_data['progress'] = (i + 1) / len(stocks) * 100
                                with open(task_file, 'w', encoding='utf-8') as f:
                                    json.dump(task_data, f, ensure_ascii=False, indent=2)
                                
                                # 避免请求过于频繁
                                time.sleep(2)
                                
                            except Exception as e:
                                task_data['failed_count'] += 1
                                # 记录失败的股票信息
                                failed_stock_info = {
                                    'code': stock['code'],
                                    'name': stock.get('name', ''),
                                    'error': str(e),
                                    'retry_count': 0
                                }
                                task_data['failed_stocks'].append(failed_stock_info)
                                task_data['stock_status'][stock['code']] = {
                                    'status': 'failed',
                                    'retry_count': 0,
                                    'error': str(e),
                                    'failed_at': datetime.utcnow().isoformat()
                                }
                                logger.error(f"分析股票 {stock['code']} 时发生错误: {str(e)}")
                        
                        # 更新任务状态为完成
                        task_data['status'] = 'completed'
                        task_data['completed_at'] = datetime.utcnow().isoformat()
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
                        
                        # 从任务管理器中注销已完成的任务
                        task_manager.unregister_task(task_id)
                        
                        # 发送完成邮件通知
                        self._send_batch_analysis_completion_email(task_data)
                        
                        logger.info(f"批量分析任务完成: {task_id}")
                    
                except Exception as e:
                    logger.error(f"批量分析任务执行失败: {task_id}, 错误: {str(e)}")
                    task_data['status'] = 'failed'
                    task_data['error'] = str(e)
                    task_data['failed_at'] = datetime.utcnow().isoformat()
                    with open(task_file, 'w', encoding='utf-8') as f:
                        json.dump(task_data, f, ensure_ascii=False, indent=2)
                    
                    # 从任务管理器中注销失败的任务
                    task_manager.unregister_task(task_id)
            
            # 启动后台线程
            analysis_thread = threading.Thread(target=run_batch_analysis)
            analysis_thread.daemon = True
            analysis_thread.start()
            
            # 注册到任务管理器
            task_manager.register_task(task_id, analysis_thread, 'batch_analysis')
            
            logger.info(f"批量分析任务已创建: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"创建批量分析任务失败: {str(e)}")
            raise e
    
    def _send_batch_analysis_completion_email(self, task_data: Dict[str, Any]):
        """发送批量分析完成邮件"""
        try:
            from flask import current_app
            from flask_mail import Message
            
            user_email = task_data['user_email']
            task_id = task_data['task_id']
            total_count = task_data['total_count']
            completed_count = task_data['completed_count']
            failed_count = task_data['failed_count']
            
            subject = f"批量分析任务完成 - {task_id}"
            body = f"""
            您的批量分析任务已完成！

            任务详情：
            - 任务ID: {task_id}
            - 总股票数: {total_count}
            - 成功分析: {completed_count}
            - 分析失败: {failed_count}
            - 完成时间: {task_data.get('completed_at', 'N/A')}

            您可以在系统中查看详细的分析报告。
            """
            
            # 这里需要配置邮件服务
            # msg = Message(subject, recipients=[user_email], body=body)
            # current_app.mail.send(msg)
            
            logger.info(f"批量分析完成邮件已发送到: {user_email}")
            
        except Exception as e:
            logger.error(f"发送批量分析完成邮件失败: {str(e)}")

    def get_task_status(self, task_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        try:
            task_file = os.path.join(self.reports_dir, f"{task_id}.task.json")
            
            if not os.path.exists(task_file):
                return None
            
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            # 检查用户权限
            if task_data.get('user_id') != user_id:
                return None
            
            return task_data
            
        except Exception as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            return None
    
    def get_user_tasks(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的任务列表"""
        try:
            tasks = []
            
            if os.path.exists(self.reports_dir):
                for file_name in os.listdir(self.reports_dir):
                    if file_name.endswith('.task.json'):
                        task_file = os.path.join(self.reports_dir, file_name)
                        try:
                            with open(task_file, 'r', encoding='utf-8') as f:
                                task_data = json.load(f)
                            
                            # 只返回当前用户的任务
                            if task_data.get('user_id') == user_id:
                                tasks.append(task_data)
                        except Exception as e:
                            logger.error(f"读取任务文件失败: {task_file}, {str(e)}")
            
            # 按创建时间排序，最新的在前
            tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return tasks[:limit]
            
        except Exception as e:
            logger.error(f"获取用户任务列表失败: {str(e)}")
            return []

    def _retry_single_task(self, task_data: Dict[str, Any]):
        """重试单个分析任务"""
        try:
            import threading
            
            def run_retry_analysis():
                from app import create_app
                app = create_app()
                with app.app_context():
                    try:
                        logger.info(f"开始重试单个分析任务: {task_data['task_id']}")
                        
                        # 更新任务状态为进行中
                        task_data['status'] = 'running'
                        task_data['started_at'] = datetime.utcnow().isoformat()
                        task_file = os.path.join(self.reports_dir, f"{task_data['task_id']}.task.json")
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
                        
                        # 执行分析（带重试机制）
                        stock_code = task_data['stock_code']
                        user_id = task_data['user_id']
                        analysis_type = task_data['analysis_type']
                        ai_provider = task_data['ai_provider']
                        
                        result = self._run_analysis_with_retry(stock_code, user_id, analysis_type, ai_provider, task_data, task_file)
                        
                        if result['success']:
                            task_data['status'] = 'completed'
                            task_data['completed_count'] = 1
                            task_data['completed_at'] = datetime.utcnow().isoformat()
                            logger.info(f"重试单个分析任务成功: {task_data['task_id']}")
                        else:
                            task_data['status'] = 'failed'
                            task_data['failed_count'] = 1
                            task_data['failed_at'] = datetime.utcnow().isoformat()
                            task_data['final_error'] = result.get('error', '分析失败')
                            logger.error(f"重试单个分析任务失败: {task_data['task_id']}, 错误: {result.get('error')}")
                        
                        # 保存最终状态
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
                            
                    except Exception as e:
                        logger.error(f"重试单个分析任务异常: {task_data['task_id']}, 错误: {str(e)}")
                        task_data['status'] = 'failed'
                        task_data['failed_at'] = datetime.utcnow().isoformat()
                        task_data['final_error'] = str(e)
                        task_file = os.path.join(self.reports_dir, f"{task_data['task_id']}.task.json")
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
            
            # 启动后台线程
            retry_thread = threading.Thread(target=run_retry_analysis)
            retry_thread.daemon = True
            retry_thread.start()
            
            logger.info(f"单个分析任务重试已启动: {task_data['task_id']}")
            
        except Exception as e:
            logger.error(f"启动单个分析任务重试失败: {str(e)}")
            raise e

    def _retry_batch_task(self, task_data: Dict[str, Any]):
        """重试批量分析任务"""
        try:
            import threading
            
            def run_retry_batch_analysis():
                from app import create_app
                app = create_app()
                with app.app_context():
                    try:
                        logger.info(f"开始重试批量分析任务: {task_data['task_id']}")
                        
                        # 更新任务状态为进行中
                        task_data['status'] = 'running'
                        task_data['started_at'] = datetime.utcnow().isoformat()
                        task_file = os.path.join(self.reports_dir, f"{task_data['task_id']}.task.json")
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
                        
                        # 逐个分析股票
                        stocks = task_data['stocks']
                        for i, stock in enumerate(stocks):
                            try:
                                stock_code = stock['code']
                                logger.info(f"重试分析股票 {i+1}/{len(stocks)}: {stock_code}")
                                
                                # 执行分析（带重试机制）
                                result = self._run_analysis_with_retry_for_batch(stock_code, task_data['user_id'], 
                                                                               task_data['analysis_type'], task_data['ai_provider'], 
                                                                               task_data, task_file)
                                
                                if result['success']:
                                    task_data['completed_count'] += 1
                                    task_data['stock_status'][stock_code] = {
                                        'status': 'completed',
                                        'retry_count': result.get('retry_count', 0),
                                        'completed_at': datetime.utcnow().isoformat()
                                    }
                                    logger.info(f"重试股票 {stock_code} 分析成功")
                                else:
                                    task_data['failed_count'] += 1
                                    # 记录失败的股票信息
                                    failed_stock_info = {
                                        'code': stock_code,
                                        'name': stock.get('name', ''),
                                        'error': result.get('error', '分析失败'),
                                        'retry_count': result.get('retry_count', 0)
                                    }
                                    task_data['failed_stocks'].append(failed_stock_info)
                                    task_data['stock_status'][stock_code] = {
                                        'status': 'failed',
                                        'retry_count': result.get('retry_count', 0),
                                        'error': result.get('error', '分析失败')
                                    }
                                    logger.error(f"重试股票 {stock_code} 分析失败: {result.get('error')}")
                                
                                # 更新进度
                                task_data['progress'] = ((i + 1) / len(stocks)) * 100
                                with open(task_file, 'w', encoding='utf-8') as f:
                                    json.dump(task_data, f, ensure_ascii=False, indent=2)
                                    
                            except Exception as e:
                                logger.error(f"重试分析股票 {stock_code} 异常: {str(e)}")
                                task_data['failed_count'] += 1
                                failed_stock_info = {
                                    'code': stock_code,
                                    'name': stock.get('name', ''),
                                    'error': str(e),
                                    'retry_count': 0
                                }
                                task_data['failed_stocks'].append(failed_stock_info)
                        
                        # 更新最终状态
                        if task_data['failed_count'] == 0:
                            task_data['status'] = 'completed'
                            task_data['completed_at'] = datetime.utcnow().isoformat()
                            logger.info(f"重试批量分析任务全部成功: {task_data['task_id']}")
                        else:
                            task_data['status'] = 'failed'
                            task_data['failed_at'] = datetime.utcnow().isoformat()
                            task_data['final_error'] = f"部分股票分析失败，成功: {task_data['completed_count']}，失败: {task_data['failed_count']}"
                            logger.warning(f"重试批量分析任务部分失败: {task_data['task_id']}")
                        
                        # 保存最终状态
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
                            
                    except Exception as e:
                        logger.error(f"重试批量分析任务异常: {task_data['task_id']}, 错误: {str(e)}")
                        task_data['status'] = 'failed'
                        task_data['failed_at'] = datetime.utcnow().isoformat()
                        task_data['final_error'] = str(e)
                        task_file = os.path.join(self.reports_dir, f"{task_data['task_id']}.task.json")
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, ensure_ascii=False, indent=2)
            
            # 启动后台线程
            retry_thread = threading.Thread(target=run_retry_batch_analysis)
            retry_thread.daemon = True
            retry_thread.start()
            
            logger.info(f"批量分析任务重试已启动: {task_data['task_id']}")
            
        except Exception as e:
            logger.error(f"启动批量分析任务重试失败: {str(e)}")
            raise e

    def delete_analysis_report(self, stock_code: str, report_id: str) -> bool:
        """删除分析报告"""
        try:
            logger.info(f"删除分析报告 - 股票代码: {stock_code}, 报告ID: {report_id}")
            
            # 遍历所有日期目录，查找包含该report_id的文件
            if os.path.exists(self.reports_dir):
                for date_dir in sorted(os.listdir(self.reports_dir), reverse=True):
                    date_path = os.path.join(self.reports_dir, date_dir)
                    if not os.path.isdir(date_path):
                        continue
                    
                    for filename in os.listdir(date_path):
                        if filename.endswith('.json') and report_id in filename:
                            report_file = os.path.join(date_path, filename)
                            logger.info(f"找到要删除的报告文件: {report_file}")
                            
                            try:
                                # 删除文件
                                os.remove(report_file)
                                logger.info(f"成功删除报告文件: {report_file}")
                                
                                # 检查目录是否为空，如果为空则删除目录
                                if not os.listdir(date_path):
                                    os.rmdir(date_path)
                                    logger.info(f"删除空目录: {date_path}")
                                
                                return True
                                
                            except Exception as e:
                                logger.error(f"删除报告文件失败: {report_file}, {str(e)}")
                                return False
            
            logger.warning(f"未找到report_id为 {report_id} 的报告文件")
            return False
            
        except Exception as e:
            logger.error(f"删除分析报告失败: {str(e)}")
            return False
    
    def pause_task(self, task_id: str, user_id: int) -> bool:
        """暂停任务"""
        try:
            from app.services.ai.task_manager import task_manager
            
            task_file = os.path.join(self.reports_dir, f"{task_id}.task.json")
            
            if not os.path.exists(task_file):
                logger.warning(f"任务文件不存在: {task_file}")
                return False
            
            # 读取任务数据
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            # 检查用户权限
            if task_data.get('user_id') != user_id:
                logger.warning(f"用户 {user_id} 无权限操作任务 {task_id}")
                return False
            
            # 检查任务状态
            current_status = task_data.get('status')
            if current_status not in ['pending', 'running']:
                logger.warning(f"任务 {task_id} 状态为 {current_status}，无法暂停")
                return False
            
            # 使用任务管理器暂停任务
            if task_manager.pause_task(task_id):
                # 更新任务文件状态
                task_data['status'] = 'paused'
                task_data['paused_at'] = datetime.utcnow().isoformat()
                task_data['updated_at'] = datetime.utcnow().isoformat()
                
                # 保存任务数据
                with open(task_file, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"任务 {task_id} 已暂停")
                return True
            else:
                # 如果任务管理器暂停失败（可能任务不在管理器中），直接更新文件状态
                logger.warning(f"任务管理器暂停任务失败: {task_id}，尝试直接更新文件状态")
                task_data['status'] = 'paused'
                task_data['paused_at'] = datetime.utcnow().isoformat()
                task_data['updated_at'] = datetime.utcnow().isoformat()
                
                # 保存任务数据
                with open(task_file, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"任务 {task_id} 已暂停（直接更新文件状态）")
                return True
            
        except Exception as e:
            logger.error(f"暂停任务失败: {str(e)}")
            return False
    
    def resume_task(self, task_id: str, user_id: int) -> bool:
        """恢复任务"""
        try:
            from app.services.ai.task_manager import task_manager
            
            task_file = os.path.join(self.reports_dir, f"{task_id}.task.json")
            
            if not os.path.exists(task_file):
                logger.warning(f"任务文件不存在: {task_file}")
                return False
            
            # 读取任务数据
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            # 检查用户权限
            if task_data.get('user_id') != user_id:
                logger.warning(f"用户 {user_id} 无权限操作任务 {task_id}")
                return False
            
            # 检查任务状态
            current_status = task_data.get('status')
            if current_status != 'paused':
                logger.warning(f"任务 {task_id} 状态为 {current_status}，无法恢复")
                return False
            
            # 使用任务管理器恢复任务
            if task_manager.resume_task(task_id):
                # 更新任务文件状态
                task_data['status'] = 'running'
                task_data['resumed_at'] = datetime.utcnow().isoformat()
                task_data['updated_at'] = datetime.utcnow().isoformat()
                
                # 保存任务数据
                with open(task_file, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"任务 {task_id} 已恢复")
                return True
            else:
                # 如果任务管理器恢复失败（可能任务不在管理器中），直接更新文件状态
                logger.warning(f"任务管理器恢复任务失败: {task_id}，尝试直接更新文件状态")
                task_data['status'] = 'running'
                task_data['resumed_at'] = datetime.utcnow().isoformat()
                task_data['updated_at'] = datetime.utcnow().isoformat()
                
                # 保存任务数据
                with open(task_file, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"任务 {task_id} 已恢复（直接更新文件状态）")
                return True
            
        except Exception as e:
            logger.error(f"恢复任务失败: {str(e)}")
            return False
    
    def delete_task(self, task_id: str, user_id: int) -> bool:
        """删除任务"""
        try:
            from app.services.ai.task_manager import task_manager
            
            task_file = os.path.join(self.reports_dir, f"{task_id}.task.json")
            
            if not os.path.exists(task_file):
                logger.warning(f"任务文件不存在: {task_file}")
                return False
            
            # 读取任务数据
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            # 检查用户权限
            if task_data.get('user_id') != user_id:
                logger.warning(f"用户 {user_id} 无权限操作任务 {task_id}")
                return False
            
            # 如果任务正在运行或暂停，先停止任务
            current_status = task_data.get('status')
            if current_status in ['pending', 'running', 'paused']:
                logger.info(f"任务 {task_id} 状态为 {current_status}，先停止任务")
                task_manager.stop_task(task_id)
                task_manager.unregister_task(task_id)
            
            # 删除任务文件
            os.remove(task_file)
            
            # 删除相关的报告文件（如果有的话）
            try:
                # 获取任务相关的股票代码
                stocks = task_data.get('stocks', [])
                if not stocks and task_data.get('stock_code'):
                    # 单个分析任务
                    stocks = [{'code': task_data.get('stock_code')}]
                
                # 删除相关报告文件
                for stock in stocks:
                    stock_code = stock.get('code')
                    if stock_code:
                        self._delete_task_reports(task_id, stock_code)
                        
            except Exception as e:
                logger.warning(f"删除任务相关报告文件时出错: {str(e)}")
            
            logger.info(f"任务 {task_id} 已删除")
            return True
            
        except Exception as e:
            logger.error(f"删除任务失败: {str(e)}")
            return False
    
    def _delete_task_reports(self, task_id: str, stock_code: str):
        """删除任务相关的报告文件"""
        try:
            reports_dir = 'data/reports'
            if not os.path.exists(reports_dir):
                return
            
            # 遍历所有日期目录
            for date_dir in os.listdir(reports_dir):
                date_path = os.path.join(reports_dir, date_dir)
                if not os.path.isdir(date_path):
                    continue
                
                # 查找匹配的报告文件
                for filename in os.listdir(date_path):
                    if filename.startswith(f'{stock_code}_') and filename.endswith('.json'):
                        file_path = os.path.join(date_path, filename)
                        
                        # 读取文件内容，检查是否属于该任务
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                report_data = json.load(f)
                            
                            # 如果报告属于该任务，删除文件
                            if report_data.get('task_id') == task_id:
                                os.remove(file_path)
                                logger.info(f"删除任务相关报告文件: {file_path}")
                                
                        except Exception as e:
                            logger.warning(f"读取报告文件失败: {file_path}, {str(e)}")
                            
        except Exception as e:
            logger.error(f"删除任务相关报告文件失败: {str(e)}")
