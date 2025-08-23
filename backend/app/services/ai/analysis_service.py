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
            from app.config.prompts import PROMPT_CONFIG
            
            if prompt_type == 'fundamental':
                return PROMPT_CONFIG['user_prompt_1']
            elif prompt_type == 'technical':
                return PROMPT_CONFIG['user_prompt_2']
            else:
                return PROMPT_CONFIG['stock_analysis']
                
        except ImportError:
            # 如果无法导入配置，返回默认提示词
            return """请对股票 ${code} (${name}) 进行专业的投资分析。

股票信息：
- 代码：${code}
- 名称：${name}
- 市场：${market}
- 行业：${industry}
- 交易所：${exchange}
- 分析日期：${analysis_date}

请从以下几个方面进行分析：

## 1. 技术面分析
- 当前价格趋势
- 支撑位和阻力位
- 技术指标分析
- 成交量分析

## 2. 基本面分析
- 公司财务状况
- 行业地位和竞争优势
- 增长前景
- 风险评估

## 3. 投资建议
- 买入/持有/卖出建议
- 目标价格区间
- 投资时间框架
- 风险提示

## 4. 市场展望
- 行业发展趋势
- 宏观经济影响
- 短期和长期展望

请提供详细、专业的分析，使用中文回答。"""
    
    def create_analysis_task(self, stock_code: str, user_id: int) -> str:
        """创建分析任务"""
        task_id = f"{stock_code}_{user_id}_{int(datetime.utcnow().timestamp())}"
        logger.info(f"创建分析任务: {task_id}")
        return task_id
    
    def run_analysis(self, stock_code: str, user_id: int, analysis_type: str = 'default') -> Dict[str, Any]:
        """运行分析（同步版本）"""
        try:
            # 获取股票信息
            stock = self.stock_repo.get_by_code(stock_code)
            if not stock:
                raise Exception(f"股票不存在: {stock_code}")
            
            # 生成分析报告
            report_data = self._generate_analysis_report(stock, analysis_type)
            
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
    
    def _generate_analysis_report(self, stock, analysis_type: str = 'default') -> Dict[str, Any]:
        """生成分析报告"""
        try:
            from app.services.ai.llm_provider import LLMProviderFactory
            from flask import current_app
            
            # 获取默认AI提供商配置
            default_provider = current_app.config.get('DEFAULT_AI_PROVIDER', 'gemini')
            
            # 根据提供商类型获取配置
            if default_provider == 'gemini':
                provider_config = {
                    'name': 'gemini',
                    'api_key': current_app.config.get('GEMINI_API_KEY'),
                    'model': current_app.config.get('GEMINI_MODEL', 'gemini-2.0-flash'),
                    'max_tokens': 2000,
                    'temperature': 0.7
                }
            elif default_provider == 'chatgpt':
                provider_config = {
                    'name': 'chatgpt',
                    'api_key': current_app.config.get('OPENAI_API_KEY'),
                    'model': current_app.config.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
                    'max_tokens': 2000,
                    'temperature': 0.7
                }
            elif default_provider == 'qwen':
                provider_config = {
                    'name': 'qwen',
                    'api_key': current_app.config.get('QWEN_API_KEY'),
                    'model': current_app.config.get('QWEN_MODEL', 'qwen-turbo'),
                    'max_tokens': 2000,
                    'temperature': 0.7
                }
            elif default_provider == 'deepseek':
                provider_config = {
                    'name': 'deepseek',
                    'api_key': current_app.config.get('DEEPSEEK_API_KEY'),
                    'model': current_app.config.get('DEEPSEEK_MODEL', 'deepseek-chat'),
                    'max_tokens': 2000,
                    'temperature': 0.7
                }
            else:
                # 默认使用Gemini
                provider_config = {
                    'name': 'gemini',
                    'api_key': current_app.config.get('GEMINI_API_KEY'),
                    'model': current_app.config.get('GEMINI_MODEL', 'gemini-2.0-flash'),
                    'max_tokens': 2000,
                    'temperature': 0.7
                }
            
            # 如果没有API密钥，返回模拟数据
            if not provider_config['api_key']:
                return {
                    'stock_code': stock.code,
                    'stock_name': stock.name,
                    'market': stock.market,
                    'analysis_date': datetime.utcnow().strftime('%Y-%m-%d'),
                    'content': f"# {stock.name} ({stock.code}) 分析报告\n\n## 技术面分析\n\n## 基本面分析\n\n## 投资建议\n\n## 市场展望",
                    'provider': 'demo',
                    'metadata': {
                        'timestamp': datetime.utcnow().isoformat(),
                        'note': f'请配置{default_provider.upper()}_API_KEY环境变量以使用真实AI分析'
                    }
                }
            
            # 创建Provider
            provider = LLMProviderFactory.create_provider(default_provider, provider_config)
            
            # 准备股票信息
            stock_info = {
                'code': stock.code,
                'name': stock.name,
                'market': stock.market,
                'industry': stock.industry or '未知',
                'exchange': stock.exchange or '未知',
                'analysis_date': datetime.utcnow().strftime('%Y-%m-%d')
            }
            
            # 生成分析报告
            prompt_template = self._get_analysis_prompt(analysis_type)
            result = provider.generate_analysis(prompt_template, stock_info)
            
            if result['success']:
                return {
                    'stock_code': stock.code,
                    'stock_name': stock.name,
                    'market': stock.market,
                    'analysis_date': stock_info['analysis_date'],
                    'content': result['content'],
                    'provider': 'gemini',
                    'metadata': {
                        'tokens_used': result.get('tokens_used'),
                        'response_time': result.get('response_time'),
                        'model': result.get('model'),
                        'timestamp': result.get('timestamp')
                    }
                }
            else:
                # 如果AI分析失败，返回错误信息
                return {
                    'stock_code': stock.code,
                    'stock_name': stock.name,
                    'market': stock.market,
                    'analysis_date': datetime.utcnow().strftime('%Y-%m-%d'),
                    'content': f"# {stock.name} ({stock.code}) 分析报告\n\n## 分析失败\n\nAI分析服务暂时不可用，请稍后重试。\n\n错误信息：{result.get('error', '未知错误')}",
                    'provider': 'gemini',
                    'metadata': {
                        'error': result.get('error'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"生成分析报告失败: {str(e)}")
            return {
                'stock_code': stock.code,
                'stock_name': stock.name,
                'market': stock.market,
                'analysis_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'content': f"# {stock.name} ({stock.code}) 分析报告\n\n## 分析失败\n\n生成分析报告时发生错误：{str(e)}",
                'provider': 'error',
                'metadata': {
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
    
    def save_analysis_report(self, stock_code: str, report_data: Dict[str, Any]) -> str:
        """保存分析报告到文件"""
        try:
            # 创建日期目录
            date_str = datetime.utcnow().strftime('%Y-%m-%d')
            date_dir = os.path.join(self.reports_dir, date_str)
            os.makedirs(date_dir, exist_ok=True)
            
            # 保存报告文件
            report_file = os.path.join(date_dir, f"{stock_code}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存分析报告: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"保存分析报告失败: {str(e)}")
            raise
    
    def get_analysis_report(self, stock_code: str, date: str = None) -> Optional[Dict[str, Any]]:
        """获取分析报告"""
        try:
            if not date:
                date = datetime.utcnow().strftime('%Y-%m-%d')
            
            report_file = os.path.join(self.reports_dir, date, f"{stock_code}.json")
            
            if os.path.exists(report_file):
                with open(report_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return None
                
        except Exception as e:
            logger.error(f"获取分析报告失败: {str(e)}")
            return None
    
    def get_user_reports(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户的分析报告"""
        try:
            reports = []
            
            # 获取用户关注的股票
            user_stocks = self.watchlist_repo.get_user_stock_codes(user_id)
            
            # 遍历报告目录
            if os.path.exists(self.reports_dir):
                for date_dir in sorted(os.listdir(self.reports_dir), reverse=True):
                    date_path = os.path.join(self.reports_dir, date_dir)
                    if not os.path.isdir(date_path):
                        continue
                    
                    for file_name in os.listdir(date_path):
                        if file_name.endswith('.json'):
                            stock_code = file_name.replace('.json', '')
                            if stock_code in user_stocks:
                                report_file = os.path.join(date_path, file_name)
                                try:
                                    with open(report_file, 'r', encoding='utf-8') as f:
                                        report_data = json.load(f)
                                        report_data['date'] = date_dir
                                        report_data['stock_code'] = stock_code
                                        reports.append(report_data)
                                except Exception as e:
                                    logger.error(f"读取报告文件失败: {report_file}, {str(e)}")
                    
                    if len(reports) >= limit:
                        break
            
            return reports[:limit]
            
        except Exception as e:
            logger.error(f"获取用户报告失败: {str(e)}")
            return []
