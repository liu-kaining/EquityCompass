# EquityCompass 模板使用指南

## 🎯 为什么选择模板化复制？

模板化复制策略具有以下优势：

### ✅ 主要优势
1. **完全控制代码** - 你可以根据新项目需求自由修改
2. **学习成本低** - 直接复制现有代码，不需要学习新的包管理
3. **快速启动** - 立即就能开始新项目开发
4. **定制化强** - 可以针对不同项目做专门优化
5. **无依赖风险** - 不依赖外部包，避免版本冲突
6. **易于调试** - 所有代码都在你的控制下，便于调试和修改

### 🚀 快速开始

#### 1. 复制模板
```bash
# 方法一：直接复制
cp -r equitycompass-template/ my-new-project/
cd my-new-project/

# 方法二：使用脚本
python scripts/setup_project.py my-new-project
```

#### 2. 自定义项目
```bash
# 运行设置脚本
python scripts/setup_project.py my-new-project

# 或者手动修改
sed -i 's/equitycompass/my-new-project/g' *.py *.md *.yml
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 初始化数据库
```bash
python scripts/init_db.py init
```

#### 5. 启动项目
```bash
python run.py
```

## 📁 模板结构详解

```
equitycompass-template/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── services/          # 核心服务模块
│   │   │   ├── auth/         # 认证服务
│   │   │   │   ├── jwt_service.py      # JWT Token 管理
│   │   │   │   ├── verification_service.py  # 验证码服务
│   │   │   │   ├── auth_service.py     # 认证服务
│   │   │   │   └── permissions.py      # 权限控制
│   │   │   ├── ai/           # AI 服务
│   │   │   │   ├── llm_provider.py     # LLM 提供商
│   │   │   │   ├── task_manager.py     # 任务管理
│   │   │   │   └── analysis_service.py # 分析服务
│   │   │   └── data/         # 数据服务
│   │   ├── api/              # API 接口
│   │   │   ├── auth_api.py   # 认证 API
│   │   │   ├── ai_api.py     # AI API
│   │   │   └── ...
│   │   ├── models/           # 数据模型
│   │   │   ├── user.py       # 用户模型
│   │   │   ├── stock.py      # 股票模型
│   │   │   └── ...
│   │   ├── templates/        # 前端模板
│   │   │   ├── components/   # 可复用组件
│   │   │   │   └── confirm_modal.html  # 确认弹窗
│   │   │   ├── auth/         # 认证页面
│   │   │   ├── dashboard/    # 仪表板
│   │   │   └── ...
│   │   └── static/           # 静态资源
│   │       ├── js/
│   │       │   └── main.js   # 核心 JavaScript 功能
│   │       └── css/
│   │           └── style.css # 核心样式
│   ├── requirements.txt      # Python 依赖
│   └── run.py               # 启动脚本
├── scripts/                  # 工具脚本
│   ├── setup_project.py     # 项目设置脚本
│   ├── init_db.py          # 数据库初始化
│   └── ...
├── docker/                   # Docker 配置
├── docs/                     # 文档
└── README.md                # 项目说明
```

## 🔧 核心功能使用

### 1. 认证系统

#### JWT Token 管理
```python
from backend.app.services.auth import JWTService

# 初始化服务
jwt_service = JWTService(secret_key="your-secret-key")

# 生成 Token
token_data = jwt_service.generate_token(
    user_id=123,
    user_data={"username": "john", "role": "admin"}
)

# 验证 Token
payload = jwt_service.verify_token(token_data["token"])
if payload:
    print(f"用户ID: {payload['user_id']}")
```

#### 权限控制装饰器
```python
from backend.app.services.auth import jwt_required, admin_required

@app.route('/api/admin/users')
@jwt_required
@admin_required
def get_users():
    # 只有管理员可以访问
    return jsonify({"users": []})
```

### 2. AI 服务

#### LLM 提供商
```python
from backend.app.services.ai import LLMProviderFactory

# 创建 AI 提供商
config = {
    "name": "qwen",
    "model": "qwen-turbo",
    "api_key": "your-api-key",
    "max_tokens": 15000,
    "temperature": 0.7
}

provider = LLMProviderFactory.create_provider("qwen", config)

# 生成分析
result = provider.generate_analysis(
    prompt="请分析这只股票的投资价值",
    stock_info={"code": "AAPL", "name": "苹果公司"}
)

if result.success:
    print(f"分析结果: {result.content}")
    print(f"使用Token: {result.tokens_used}")
else:
    print(f"分析失败: {result.error}")
```

#### 任务管理
```python
from backend.app.services.ai import TaskManager

# 创建任务管理器
task_manager = TaskManager()

# 提交异步任务
def analysis_task():
    # 你的分析逻辑
    pass

task_id = task_manager.submit_task("analysis_001", analysis_task)
```

### 3. 前端组件

#### 确认弹窗
```html
<!-- 在模板中包含弹窗组件 -->
{% include 'components/confirm_modal.html' %}

<!-- 使用确认弹窗 -->
<button onclick="confirmAction('确认删除', '确定要删除这个项目吗？', deleteFunction)">
    删除项目
</button>

<script>
function deleteFunction() {
    // 删除逻辑
    console.log('用户确认删除');
}
</script>
```

#### Markdown 渲染
```python
from backend.app.services.ui import MarkdownRenderer

# 在视图中使用
@app.route('/article/<int:article_id>')
def show_article(article_id):
    article = Article.query.get(article_id)
    renderer = MarkdownRenderer()
    html_content = renderer.render(article.content)
    return render_template('article.html', content=html_content)
```

```html
<!-- 在模板中显示 -->
<div class="markdown-content">
    {{ content | safe }}
</div>
```

## 🎨 自定义指南

### 修改项目名称
```bash
# 使用脚本自动修改
python scripts/setup_project.py my-new-project

# 或手动修改
find . -type f -name "*.py" -exec sed -i 's/equitycompass/my-new-project/g' {} \;
find . -type f -name "*.md" -exec sed -i 's/equitycompass/my-new-project/g' {} \;
find . -type f -name "*.yml" -exec sed -i 's/equitycompass/my-new-project/g' {} \;
```

### 添加新功能
1. **创建新的服务模块**
```python
# backend/app/services/your_service.py
class YourService:
    def __init__(self):
        # 初始化你的服务
        pass
    
    def your_method(self):
        # 你的业务逻辑
        pass
```

2. **创建新的 API 接口**
```python
# backend/app/api/your_api.py
from flask import Blueprint, request, jsonify
from backend.app.services.your_service import YourService

your_api = Blueprint('your_api', __name__)

@your_api.route('/api/your-endpoint', methods=['POST'])
def your_endpoint():
    service = YourService()
    result = service.your_method()
    return jsonify({"success": True, "data": result})
```

3. **创建新的数据模型**
```python
# backend/app/models/your_model.py
from backend.app import db

class YourModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 修改数据库
1. **添加新的数据模型**
2. **运行数据库迁移**
```bash
python scripts/init_db.py init
```

### 自定义前端样式
```css
/* backend/app/static/css/custom.css */
.your-custom-class {
    /* 你的自定义样式 */
}

/* 覆盖默认样式 */
.markdown-content {
    /* 自定义 Markdown 样式 */
}
```

## 🔒 安全配置

### 环境变量配置
```bash
# .env 文件
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///app.db
QWEN_API_KEY=your-qwen-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 生产环境配置
```python
# backend/app/config/production.py
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEBUG = False
    
    # AI 配置
    QWEN_API_KEY = os.environ.get('QWEN_API_KEY')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
```

## 🚀 部署

### Docker 部署
```bash
# 构建镜像
docker build -t my-new-project .

# 运行容器
docker run -p 5000:5000 my-new-project
```

### 传统部署
```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py init

# 启动应用
python run.py
```

## 📊 性能优化

### 1. 数据库优化
```python
# 使用连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@localhost/db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 2. 缓存策略
```python
# 使用 Redis 缓存
import redis
from backend.app.services.ai import LLMProviderFactory

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
        
        # 生成新结果并缓存
        result = self.provider.generate_analysis(prompt, stock_info)
        if result.success:
            self.redis_client.setex(cache_key, 3600, json.dumps(result.__dict__))
        
        return result
```

### 3. 异步处理
```python
# 使用 Celery 进行异步任务处理
from celery import Celery
from backend.app.services.ai import LLMProviderFactory

celery_app = Celery('myapp')

@celery_app.task
def analyze_stock_async(stock_code, prompt):
    provider = LLMProviderFactory.create_default_provider()
    result = provider.generate_analysis(prompt, {"code": stock_code})
    return result.__dict__
```

## 🧪 测试

### 单元测试
```python
# tests/test_auth.py
import pytest
from backend.app.services.auth import JWTService

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

### 集成测试
```python
# tests/test_integration.py
import pytest
from backend.app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

def test_auth_endpoint(client):
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
```

## 📝 开发最佳实践

### 1. 代码规范
```bash
# 使用 Black 格式化代码
black backend/

# 使用 Flake8 检查代码质量
flake8 backend/

# 使用 mypy 进行类型检查
mypy backend/
```

### 2. 版本控制
```bash
# 初始化 Git 仓库
git init
git add .
git commit -m "Initial commit"

# 创建开发分支
git checkout -b develop
```

### 3. 文档编写
```python
def your_function(param1: str, param2: int) -> dict:
    """
    你的函数说明
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
        
    Returns:
        返回值说明
        
    Raises:
        ValueError: 当参数无效时抛出
    """
    pass
```

## 🎯 总结

模板化复制策略的优势：

1. **快速启动** - 立即就能开始新项目开发
2. **完全控制** - 所有代码都在你的控制下
3. **易于定制** - 可以根据项目需求自由修改
4. **学习成本低** - 直接使用现有代码，无需学习新框架
5. **无依赖风险** - 不依赖外部包，避免版本冲突

这个策略特别适合：
- 快速原型开发
- 小型到中型项目
- 需要完全控制代码的项目
- 团队对现有代码熟悉的情况

通过这个模板，你可以快速启动新项目，同时保留 EquityCompass 项目的所有优秀功能！
