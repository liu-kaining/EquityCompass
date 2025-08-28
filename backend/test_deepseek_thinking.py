#!/usr/bin/env python3
"""
测试 DeepSeek 深度思考功能
"""
import os
import sys
import logging
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai.llm_provider import DeepSeekProvider, LLMProviderFactory

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_deepseek_thinking():
    """测试 DeepSeek 深度思考功能"""
    
    # 检查环境变量
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        logger.error("请设置 DEEPSEEK_API_KEY 环境变量")
        return False
    
    # 配置 DeepSeek Provider
    config = {
        'name': 'deepseek',
        'api_key': api_key,
        'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner'),
        'max_tokens': 8000,
        'temperature': 0.7,
        'enable_deep_thinking': True,
        'thinking_steps': int(os.getenv('DEEPSEEK_THINKING_STEPS', '3'))
    }
    
    logger.info(f"DeepSeek 配置: {config}")
    
    try:
        # 创建 Provider
        provider = DeepSeekProvider(config)
        
        # 测试连接
        logger.info("测试 DeepSeek 连接...")
        if provider.test_connection():
            logger.info("✅ DeepSeek 连接测试成功")
        else:
            logger.error("❌ DeepSeek 连接测试失败")
            return False
        
        # 测试深度思考分析
        logger.info("测试深度思考分析...")
        
        # 模拟股票信息
        stock_info = {
            'code': '000001',
            'name': '平安银行',
            'market': '深圳',
            'industry': '银行',
            'exchange': 'SZSE',
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # 分析提示词
        prompt = """
请对 ${name} (${code}) 进行专业的股票分析。

股票信息：
- 代码：${code}
- 名称：${name}
- 市场：${market}
- 行业：${industry}
- 交易所：${exchange}
- 分析日期：${analysis_date}

请从以下方面进行分析：
1. 基本面分析
2. 技术面分析
3. 风险评估
4. 投资建议

请提供详细的分析报告。
"""
        
        # 生成分析
        result = provider.generate_analysis(prompt, stock_info)
        
        if result['success']:
            logger.info("✅ 深度思考分析成功")
            logger.info(f"内容长度: {len(result['content'])} 字符")
            logger.info(f"使用模型: {result.get('model')}")
            logger.info(f"Token使用: {result.get('tokens_used')}")
            logger.info(f"响应时间: {result.get('response_time', 0):.2f}秒")
            
            # 显示部分内容
            content_preview = result['content'][:500] + "..." if len(result['content']) > 500 else result['content']
            logger.info(f"分析内容预览:\n{content_preview}")
            
            return True
        else:
            logger.error(f"❌ 深度思考分析失败: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {str(e)}")
        return False

def test_without_thinking():
    """测试不使用深度思考的情况"""
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        logger.error("请设置 DEEPSEEK_API_KEY 环境变量")
        return False
    
    # 配置 DeepSeek Provider（不启用深度思考）
    config = {
        'name': 'deepseek',
        'api_key': api_key,
        'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner'),
        'max_tokens': 8000,
        'temperature': 0.7,
        'enable_deep_thinking': False  # 不启用深度思考
    }
    
    logger.info(f"DeepSeek 配置（无深度思考）: {config}")
    
    try:
        provider = DeepSeekProvider(config)
        
        stock_info = {
            'code': '000002',
            'name': '万科A',
            'market': '深圳',
            'industry': '房地产',
            'exchange': 'SZSE',
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        prompt = "请简要分析 ${name} (${code}) 的投资价值。"
        
        result = provider.generate_analysis(prompt, stock_info)
        
        if result['success']:
            logger.info("✅ 普通分析成功")
            logger.info(f"内容长度: {len(result['content'])} 字符")
            return True
        else:
            logger.error(f"❌ 普通分析失败: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("开始测试 DeepSeek 深度思考功能...")
    
    # 测试深度思考
    thinking_success = test_deepseek_thinking()
    
    # 测试普通模式
    normal_success = test_without_thinking()
    
    if thinking_success and normal_success:
        logger.info("🎉 所有测试通过！")
    else:
        logger.error("❌ 部分测试失败")
        sys.exit(1)
