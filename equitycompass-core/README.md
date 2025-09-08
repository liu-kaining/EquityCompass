# EquityCompass Core

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/equitycompass-core.svg)](https://pypi.org/project/equitycompass-core/)

可复用的核心功能模块：认证、AI代理、异步任务、UI组件

## 🚀 功能特性

### 🔐 用户认证系统
- **JWT Token 管理**：完整的 Token 生成、验证、刷新机制
- **邮箱验证码登录**：无密码登录，安全便捷
- **权限控制系统**：三级权限管理（SUPER_ADMIN、SITE_ADMIN、USER）
- **Session 管理**：传统页面访问支持

### 🤖 多模型AI代理系统
- **LLM Provider 抽象层**：支持多种AI模型（Qwen、DeepSeek、OpenAI等）
- **策略模式设计**：易于扩展新的AI提供商
- **重试机制**：指数退避策略，自动故障转移
- **配置管理**：数据库驱动的模型配置

### ⚡ 异步任务系统
- **任务管理器**：支持任务暂停、恢复、取消
- **状态跟踪**：完整的任务生命周期管理
- **错误处理**：完善的异常处理和重试逻辑
- **进度监控**：实时任务状态更新

### 🎨 前端UI组件库
- **Markdown 渲染器**：完整的 Markdown 解析和样式
- **弹窗组件系统**：确认弹窗、警告弹窗、加载弹窗
- **响应式设计**：Bootstrap 5 + 自定义样式
- **交互工具**：加载状态、Toast提示、工具提示

## 📦 安装

```bash
pip install equitycompass-core
```

## 🛠️ 快速开始

### 认证服务

```python
from equitycompass.auth import AuthService, JWTService

# 初始化认证服务
auth = AuthService()
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

### AI 服务

```python
from equitycompass.ai import LLMProvider, LLMProviderFactory

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

### UI 组件

```python
from equitycompass.ui import MarkdownRenderer, ConfirmModal, ModalManager

# Markdown 渲染
renderer = MarkdownRenderer()
html = renderer.render("# 标题\n\n这是**粗体**文本")

# 弹窗管理
modal_manager = ModalManager()
confirm_modal = modal_manager.create_confirm_modal(
    title="确认删除",
    message="确定要删除这个项目吗？"
)

# 生成 HTML 和 JavaScript
html_content = modal_manager.generate_all_html()
js_content = modal_manager.generate_all_js()
```

### Flask 集成

```python
from flask import Flask, request, jsonify
from equitycompass.auth import jwt_required, get_current_user
from equitycompass.ai import LLMProviderFactory

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
@jwt_required
def analyze():
    user = get_current_user()
    
    # 创建 AI 提供商
    provider = LLMProviderFactory.create_default_provider()
    
    # 执行分析
    result = provider.generate_analysis(
        prompt=request.json['prompt'],
        stock_info=request.json['stock_info']
    )
    
    return jsonify({
        'success': result.success,
        'content': result.content if result.success else None,
        'error': result.error if not result.success else None
    })
```

## 📚 API 文档

### 认证模块

#### JWTService

```python
class JWTService:
    def generate_token(self, user_id: int, user_data: Dict = None, expiry: int = None) -> Dict
    def verify_token(self, token: str) -> Optional[Dict]
    def refresh_token(self, refresh_token: str) -> Optional[Dict]
    def extract_user_id(self, token: str) -> Optional[int]
    def is_token_expired(self, token: str) -> bool
```

#### 装饰器

```python
@jwt_required  # JWT 认证装饰器
def protected_route():
    pass
```

### AI 模块

#### LLMProvider

```python
class LLMProvider:
    def generate_analysis(self, prompt: str, stock_info: Dict) -> AnalysisResult
```

#### LLMProviderFactory

```python
class LLMProviderFactory:
    @classmethod
    def create_provider(cls, provider_name: str, config: Dict) -> LLMProvider
    @classmethod
    def get_available_providers(cls) -> List[str]
    @classmethod
    def create_default_provider(cls) -> LLMProvider
```

### UI 模块

#### MarkdownRenderer

```python
class MarkdownRenderer:
    def render(self, markdown_text: str, **kwargs) -> str
    def render_with_styles(self, markdown_text: str, include_css: bool = True) -> str
    def get_css_styles(self) -> str
```

#### 弹窗组件

```python
class ConfirmModal:
    def to_html(self) -> str
    def to_js(self) -> str

class AlertModal:
    def to_html(self) -> str
    def to_js(self) -> str

class LoadingModal:
    def to_html(self) -> str
    def to_js(self) -> str
    def set_progress(self, value: int)
```

## 🔧 配置

### 认证配置

```python
from equitycompass import configure

configure(
    auth={
        "jwt_secret": "your-secret-key",
        "jwt_expiry": 3600,
        "verification_code_ttl": 600,
        "max_login_attempts": 5,
    }
)
```

### AI 配置

```python
configure(
    ai={
        "providers": ["qwen", "deepseek", "openai"],
        "default_provider": "qwen",
        "retry_config": {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 60.0,
            "exponential_base": 2.0,
        },
        "timeout_config": {
            "request_timeout": 120,
            "connect_timeout": 30,
        },
    }
)
```

## 🧪 测试

```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=equitycompass

# 运行特定模块测试
pytest tests/test_auth.py
pytest tests/test_ai.py
pytest tests/test_ui.py
```

## 📝 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 代码格式化

```bash
black equitycompass/
flake8 equitycompass/
mypy equitycompass/
```

### 构建包

```bash
python setup.py sdist bdist_wheel
```

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [PyJWT](https://pyjwt.readthedocs.io/) - JWT 处理
- [Markdown](https://python-markdown.github.io/) - Markdown 解析
- [Bootstrap](https://getbootstrap.com/) - UI 框架

## 📞 支持

如果你遇到任何问题或有任何建议，请：

- 提交 [Issue](https://github.com/your-org/equitycompass-core/issues)
- 发送邮件到 team@equitycompass.com
- 查看 [文档](https://equitycompass-core.readthedocs.io/)

---

**EquityCompass Core** - 让功能复用变得简单！
