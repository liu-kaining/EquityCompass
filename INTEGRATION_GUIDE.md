# EquityCompass 功能复用集成指南

## 🎯 概述

本指南详细说明如何将 EquityCompass 项目中的核心功能模块集成到你的新项目中。我们提供了三种主要的复用策略，你可以根据项目需求选择最适合的方案。

## 📋 复用功能清单

### ✅ 高优先级功能（推荐立即复用）

| 功能模块 | 复用价值 | 复杂度 | 集成难度 |
|---------|---------|--------|----------|
| JWT 认证服务 | ⭐⭐⭐⭐⭐ | 中等 | 简单 |
| LLM Provider 抽象层 | ⭐⭐⭐⭐⭐ | 高 | 中等 |
| 确认弹窗组件 | ⭐⭐⭐⭐⭐ | 低 | 简单 |
| Markdown 渲染器 | ⭐⭐⭐⭐⭐ | 低 | 简单 |

### 🔄 中优先级功能（后续复用）

| 功能模块 | 复用价值 | 复杂度 | 集成难度 |
|---------|---------|--------|----------|
| 任务管理器 | ⭐⭐⭐⭐ | 高 | 中等 |
| 权限控制系统 | ⭐⭐⭐⭐ | 中等 | 中等 |
| 响应式设计组件 | ⭐⭐⭐⭐ | 低 | 简单 |
| 数据库抽象层 | ⭐⭐⭐ | 中等 | 中等 |

## 🚀 策略一：Python 包化（推荐）

### 优势
- ✅ 代码复用性最高
- ✅ 易于维护和更新
- ✅ 支持版本管理
- ✅ 可以发布到 PyPI

### 实施步骤

#### 1. 安装包
```bash
pip install equitycompass-core
```

#### 2. 基础集成
```python
# 在你的项目中
from equitycompass.auth import AuthService, JWTService
from equitycompass.ai import LLMProviderFactory
from equitycompass.ui import MarkdownRenderer, ConfirmModal

# 初始化服务
auth_service = AuthService()
jwt_service = JWTService(secret_key="your-secret-key")
markdown_renderer = MarkdownRenderer()
```

#### 3. Flask 应用集成
```python
from flask import Flask, request, jsonify
from equitycompass.auth import jwt_required, get_current_user

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
@jwt_required
def analyze():
    user = get_current_user()
    # 你的业务逻辑
    return jsonify({"success": True})
```

#### 4. 前端集成
```html
<!-- 在你的 HTML 模板中 -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- 包含弹窗组件 -->
<div id="confirmModal"></div>

<script>
// 使用确认弹窗
confirmAction("确认删除", "确定要删除这个项目吗？", function() {
    // 删除逻辑
});
</script>
```

### 配置示例

```python
# config.py
from equitycompass import configure

configure(
    auth={
        "jwt_secret": "your-production-secret-key",
        "jwt_expiry": 3600,
        "verification_code_ttl": 600,
    },
    ai={
        "providers": ["qwen", "deepseek"],
        "default_provider": "qwen",
        "retry_config": {
            "max_retries": 3,
            "base_delay": 1.0,
        },
    }
)
```

## 🏗️ 策略二：微服务化

### 优势
- ✅ 服务独立部署
- ✅ 支持水平扩展
- ✅ 技术栈灵活
- ✅ 适合大型项目

### 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │   AI Service    │    │  UI Components  │
│   Port: 8001    │    │   Port: 8002    │    │   Port: 8003    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  API Gateway    │
                    │   Port: 8000    │
                    └─────────────────┘
```

### 实施步骤

#### 1. 创建认证服务
```python
# auth_service/app.py
from flask import Flask, request, jsonify
from equitycompass.auth import AuthService, JWTService

app = Flask(__name__)
auth_service = AuthService()
jwt_service = JWTService()

@app.route('/auth/login', methods=['POST'])
def login():
    # 认证逻辑
    pass

@app.route('/auth/verify', methods=['POST'])
def verify():
    # 验证逻辑
    pass
```

#### 2. 创建 AI 服务
```python
# ai_service/app.py
from flask import Flask, request, jsonify
from equitycompass.ai import LLMProviderFactory

app = Flask(__name__)

@app.route('/ai/analyze', methods=['POST'])
def analyze():
    provider = LLMProviderFactory.create_default_provider()
    result = provider.generate_analysis(
        prompt=request.json['prompt'],
        stock_info=request.json['stock_info']
    )
    return jsonify({
        'success': result.success,
        'content': result.content
    })
```

#### 3. 创建 API 网关
```python
# gateway/app.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

AUTH_SERVICE_URL = "http://auth-service:8001"
AI_SERVICE_URL = "http://ai-service:8002"

@app.route('/api/auth/<path:path>', methods=['GET', 'POST'])
def auth_proxy(path):
    url = f"{AUTH_SERVICE_URL}/auth/{path}"
    response = requests.request(
        method=request.method,
        url=url,
        headers=request.headers,
        data=request.get_data(),
        params=request.args
    )
    return response.json(), response.status_code

@app.route('/api/ai/<path:path>', methods=['GET', 'POST'])
def ai_proxy(path):
    url = f"{AI_SERVICE_URL}/ai/{path}"
    response = requests.request(
        method=request.method,
        url=url,
        headers=request.headers,
        data=request.get_data(),
        params=request.args
    )
    return response.json(), response.status_code
```

#### 4. Docker 配置
```yaml
# docker-compose.yml
version: '3.8'
services:
  auth-service:
    build: ./auth_service
    ports:
      - "8001:8000"
    environment:
      - JWT_SECRET=your-secret-key
  
  ai-service:
    build: ./ai_service
    ports:
      - "8002:8000"
    environment:
      - QWEN_API_KEY=your-api-key
  
  gateway:
    build: ./gateway
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
      - ai-service
```

## 📋 策略三：模板化复制

### 优势
- ✅ 快速原型开发
- ✅ 完全控制代码
- ✅ 适合小型项目
- ✅ 学习成本低

### 实施步骤

#### 1. 下载模板
```bash
git clone https://github.com/your-org/equitycompass-template.git my-project
cd my-project
```

#### 2. 自定义配置
```python
# config.py
class Config:
    # 认证配置
    JWT_SECRET_KEY = 'your-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    # AI 配置
    QWEN_API_KEY = 'your-qwen-api-key'
    DEEPSEEK_API_KEY = 'your-deepseek-api-key'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

#### 3. 修改业务逻辑
```python
# app/services/your_service.py
from equitycompass.auth import AuthService
from equitycompass.ai import LLMProviderFactory

class YourBusinessService:
    def __init__(self):
        self.auth_service = AuthService()
        self.ai_provider = LLMProviderFactory.create_default_provider()
    
    def your_business_method(self, data):
        # 你的业务逻辑
        pass
```

#### 4. 自定义前端
```html
<!-- templates/your_page.html -->
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>你的页面标题</h1>
    
    <!-- 使用复用的组件 -->
    <div class="markdown-content">
        {{ your_markdown_content | safe }}
    </div>
    
    <button onclick="confirmAction('确认操作', '确定要执行吗？', yourFunction)">
        执行操作
    </button>
</div>
{% endblock %}
```

## 🔧 具体集成示例

### 示例1：电商项目集成

```python
# 电商项目中的用户认证
from equitycompass.auth import AuthService, JWTService

class EcommerceAuthService:
    def __init__(self):
        self.auth_service = AuthService()
        self.jwt_service = JWTService()
    
    def register_customer(self, email, password):
        # 注册客户
        user = self.auth_service.create_user(email, password)
        return user
    
    def login_customer(self, email, password):
        # 客户登录
        user = self.auth_service.authenticate_user(email, password)
        if user:
            token = self.jwt_service.generate_token(user.id)
            return token
        return None
```

### 示例2：内容管理系统集成

```python
# CMS 中的 AI 内容生成
from equitycompass.ai import LLMProviderFactory
from equitycompass.ui import MarkdownRenderer

class ContentManager:
    def __init__(self):
        self.ai_provider = LLMProviderFactory.create_provider('qwen', {
            'api_key': 'your-api-key',
            'model': 'qwen-turbo'
        })
        self.markdown_renderer = MarkdownRenderer()
    
    def generate_article(self, topic):
        prompt = f"请写一篇关于{topic}的文章"
        result = self.ai_provider.generate_analysis(prompt, {})
        
        if result.success:
            # 渲染为 HTML
            html = self.markdown_renderer.render(result.content)
            return html
        return None
```

### 示例3：数据分析平台集成

```python
# 数据分析平台中的任务管理
from equitycompass.ai import TaskManager, LLMProviderFactory

class DataAnalysisPlatform:
    def __init__(self):
        self.task_manager = TaskManager()
        self.ai_provider = LLMProviderFactory.create_default_provider()
    
    def analyze_dataset(self, dataset_id):
        task_id = f"analysis_{dataset_id}_{int(time.time())}"
        
        def analysis_task():
            # 数据分析逻辑
            result = self.ai_provider.generate_analysis(
                prompt="请分析这个数据集",
                stock_info={"dataset_id": dataset_id}
            )
            return result
        
        # 提交异步任务
        self.task_manager.submit_task(task_id, analysis_task)
        return task_id
```

## 🎨 前端集成示例

### React 集成

```jsx
// React 组件中使用确认弹窗
import React from 'react';

const MyComponent = () => {
  const handleDelete = () => {
    // 使用全局的确认弹窗函数
    if (window.confirmAction) {
      window.confirmAction(
        '确认删除',
        '确定要删除这个项目吗？',
        () => {
          // 删除逻辑
          console.log('用户确认删除');
        }
      );
    }
  };

  return (
    <button onClick={handleDelete}>
      删除项目
    </button>
  );
};
```

### Vue.js 集成

```vue
<template>
  <div>
    <button @click="showConfirm">删除项目</button>
  </div>
</template>

<script>
export default {
  methods: {
    showConfirm() {
      // 使用全局的确认弹窗函数
      if (window.confirmAction) {
        window.confirmAction(
          '确认删除',
          '确定要删除这个项目吗？',
          this.handleDelete
        );
      }
    },
    
    handleDelete() {
      // 删除逻辑
      console.log('用户确认删除');
    }
  }
}
</script>
```

## 📊 性能优化建议

### 1. 缓存策略
```python
# 使用 Redis 缓存
import redis
from equitycompass.ai import LLMProviderFactory

class CachedAIProvider:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.provider = LLMProviderFactory.create_default_provider()
    
    def generate_analysis(self, prompt, stock_info):
        # 生成缓存键
        cache_key = f"analysis:{hash(prompt)}:{stock_info.get('code')}"
        
        # 检查缓存
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # 生成新结果
        result = self.provider.generate_analysis(prompt, stock_info)
        
        # 缓存结果
        if result.success:
            self.redis_client.setex(cache_key, 3600, json.dumps(result.__dict__))
        
        return result
```

### 2. 连接池
```python
# 使用连接池优化数据库连接
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@localhost/db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 3. 异步处理
```python
# 使用 Celery 进行异步任务处理
from celery import Celery
from equitycompass.ai import LLMProviderFactory

celery_app = Celery('myapp')

@celery_app.task
def analyze_stock_async(stock_code, prompt):
    provider = LLMProviderFactory.create_default_provider()
    result = provider.generate_analysis(prompt, {"code": stock_code})
    return result.__dict__
```

## 🔒 安全考虑

### 1. JWT 安全
```python
# 安全的 JWT 配置
from equitycompass.auth import JWTService

jwt_service = JWTService(
    secret_key=os.environ.get('JWT_SECRET_KEY'),  # 使用环境变量
    algorithm='HS256'
)

# 设置合理的过期时间
token_data = jwt_service.generate_token(
    user_id=user.id,
    expiry=3600  # 1小时过期
)
```

### 2. API 密钥管理
```python
# 安全的 API 密钥管理
import os
from equitycompass.ai import LLMProviderFactory

config = {
    'name': 'qwen',
    'model': 'qwen-turbo',
    'api_key': os.environ.get('QWEN_API_KEY'),  # 从环境变量获取
    'max_tokens': 15000,
    'temperature': 0.7
}

provider = LLMProviderFactory.create_provider('qwen', config)
```

### 3. 输入验证
```python
# 输入验证和清理
from equitycompass.ui import MarkdownRenderer
import bleach

class SafeMarkdownRenderer(MarkdownRenderer):
    def render(self, markdown_text, **kwargs):
        # 清理 HTML 标签
        html = super().render(markdown_text, **kwargs)
        cleaned_html = bleach.clean(html, tags=['p', 'h1', 'h2', 'h3', 'strong', 'em'])
        return cleaned_html
```

## 🧪 测试策略

### 1. 单元测试
```python
# tests/test_auth.py
import pytest
from equitycompass.auth import JWTService

def test_jwt_token_generation():
    jwt_service = JWTService(secret_key="test-secret")
    token_data = jwt_service.generate_token(user_id=123)
    
    assert token_data['token'] is not None
    assert token_data['expires_in'] == 3600

def test_jwt_token_verification():
    jwt_service = JWTService(secret_key="test-secret")
    token_data = jwt_service.generate_token(user_id=123)
    
    payload = jwt_service.verify_token(token_data['token'])
    assert payload['user_id'] == 123
```

### 2. 集成测试
```python
# tests/test_integration.py
import pytest
from equitycompass.ai import LLMProviderFactory

def test_ai_provider_integration():
    config = {
        'name': 'qwen',
        'model': 'qwen-turbo',
        'api_key': 'test-api-key',
    }
    
    provider = LLMProviderFactory.create_provider('qwen', config)
    result = provider.generate_analysis("测试提示", {"code": "TEST"})
    
    # 注意：这里可能需要 mock API 调用
    assert result is not None
```

## 📈 监控和日志

### 1. 日志配置
```python
# 配置日志
import logging
from equitycompass.ai import LLMProvider

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 在 AI 提供商中添加日志
class LoggedLLMProvider(LLMProvider):
    def generate_analysis(self, prompt, stock_info):
        logger.info(f"开始分析: {stock_info.get('code')}")
        result = super().generate_analysis(prompt, stock_info)
        logger.info(f"分析完成: {result.success}")
        return result
```

### 2. 性能监控
```python
# 性能监控
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"{func.__name__} 执行时间: {end_time - start_time:.2f}秒")
        return result
    return wrapper

# 使用装饰器
@monitor_performance
def analyze_stock(stock_code):
    # 分析逻辑
    pass
```

## 🎯 总结

通过以上三种策略，你可以有效地将 EquityCompass 项目中的核心功能复用到你的新项目中：

1. **Python 包化** - 最适合代码复用，易于维护
2. **微服务化** - 最适合大型项目，支持独立部署  
3. **模板化复制** - 最适合快速原型开发

选择哪种策略取决于你的项目规模、团队技术栈和长期维护计划。建议从 **Python 包化** 开始，随着项目发展再考虑其他策略。

记住，功能复用的关键是保持代码的模块化和可配置性，这样你就能在不同的项目中灵活使用这些功能。
