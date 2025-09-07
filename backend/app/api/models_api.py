"""
模型管理API
提供模型列表、模型信息等功能
"""
from flask import Blueprint, jsonify, request
from app.utils.response import success_response, error_response
from app.services.ai.llm_provider import LLMProviderFactory
import logging

logger = logging.getLogger(__name__)

models_bp = Blueprint('models', __name__, url_prefix='/api/models')


@models_bp.route('/providers', methods=['GET'])
def get_providers():
    """获取可用的Provider列表"""
    try:
        providers = LLMProviderFactory.get_available_providers()
        return success_response(providers)
    except Exception as e:
        logger.error(f"获取Provider列表失败: {str(e)}")
        return error_response("获取Provider列表失败", str(e))


@models_bp.route('/<provider>', methods=['GET'])
def get_models(provider):
    """获取指定Provider的可用模型列表"""
    try:
        models = LLMProviderFactory.get_available_models(provider)
        if not models:
            return error_response(f"Provider '{provider}' 不存在或没有可用模型")
        
        return success_response(models)
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return error_response("获取模型列表失败", str(e))


@models_bp.route('/<provider>/<model>', methods=['GET'])
def get_model_info(provider, model):
    """获取指定模型的详细信息"""
    try:
        models = LLMProviderFactory.get_available_models(provider)
        if not models:
            return error_response(f"Provider '{provider}' 不存在")
        
        if model not in models:
            return error_response(f"模型 '{model}' 不存在")
        
        model_info = models[model]
        return success_response(model_info)
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        return error_response("获取模型信息失败", str(e))


@models_bp.route('/test', methods=['POST'])
def test_model():
    """测试模型连接"""
    try:
        data = request.get_json()
        if not data:
            return error_response("INVALID_PARAM", "请求数据不能为空")
        
        provider = data.get('provider')
        model = data.get('model')
        api_key = data.get('api_key')
        
        if not all([provider, model, api_key]):
            return error_response("INVALID_PARAM", "provider、model和api_key都是必需的")
        
        # 创建测试配置
        config = {
            'name': f'{provider}-test',
            'api_key': api_key,
            'model': model,
            'max_tokens': 1000,
            'temperature': 0.7
        }
        
        # 测试连接
        is_available = LLMProviderFactory.test_provider(provider, config)
        
        if is_available:
            return success_response({"status": "success", "message": "模型连接测试成功"})
        else:
            return error_response("CONNECTION_FAILED", "模型连接测试失败")
            
    except Exception as e:
        logger.error(f"测试模型失败: {str(e)}")
        return error_response("INTERNAL_ERROR", f"测试模型失败: {str(e)}")


@models_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """获取模型推荐"""
    try:
        # 根据不同的使用场景推荐模型
        recommendations = {
            'quick_analysis': {
                'name': '快速分析',
                'description': '适合快速获取股票分析结果',
                'recommended_models': [
                    {'provider': 'qwen', 'model': 'qwen-turbo', 'reason': '响应速度快，成本低'},
                    {'provider': 'gemini', 'model': 'gemini-2.0-flash', 'reason': 'Google最新模型，性能优秀'}
                ]
            },
            'detailed_analysis': {
                'name': '详细分析',
                'description': '适合需要深度分析的场景',
                'recommended_models': [
                    {'provider': 'qwen', 'model': 'qwen-plus', 'reason': '平衡性能和成本'},
                    {'provider': 'deepseek', 'model': 'deepseek-chat', 'reason': '推理能力强'}
                ]
            },
            'professional_research': {
                'name': '专业研究',
                'description': '适合专业投资研究和复杂分析',
                'recommended_models': [
                    {'provider': 'qwen', 'model': 'qwen-max', 'reason': '高性能，适合复杂任务'},
                    {'provider': 'deepseek', 'model': 'deepseek-reasoner', 'reason': '专门用于推理任务'},
                    {'provider': 'qwen', 'model': 'qwen-deep-research', 'reason': '深度研究模型，支持流式输出'}
                ]
            },
            'premium_analysis': {
                'name': '顶级分析',
                'description': '适合对分析质量要求极高的场景',
                'recommended_models': [
                    {'provider': 'qwen', 'model': 'qwen-max-preview', 'reason': '最新技术，最强性能'},
                    {'provider': 'qwen', 'model': 'qwen-deep-research', 'reason': '深度研究，专业分析'}
                ]
            }
        }
        
        return success_response(recommendations)
    except Exception as e:
        logger.error(f"获取模型推荐失败: {str(e)}")
        return error_response("获取模型推荐失败", str(e))
