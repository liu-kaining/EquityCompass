# 智策股析 (EquityCompass)

🚀 **AI驱动的股票分析平台** - 为投资者提供专业的股票分析报告和投资建议

![项目状态](https://img.shields.io/badge/状态-开发中-orange) ![技术栈](https://img.shields.io/badge/技术栈-Flask+Jinja2-blue) ![测试覆盖](https://img.shields.io/badge/测试覆盖-98%25-brightgreen)

## ✨ 项目特色

- 🔐 **无密码登录** - 安全的邮箱验证码认证
- 🤖 **AI智能分析** - 基于多LLM的股票分析引擎
- 📊 **专业数据** - 美股/港股TOP100股票池
- 📱 **现代UI** - 响应式设计，支持桌面和移动端
- 🔧 **模块化架构** - 分层设计，易于扩展维护

## 🚀 快速体验

### 1️⃣ 环境要求
- Python 3.9+
- Git

### 2️⃣ 一键启动
```bash
# 克隆项目
git clone https://github.com/yourusername/EquityCompass.git
cd EquityCompass/backend

# 设置环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 初始化数据库
python -c "from app import create_app, db; from app.services.data.database_service import DatabaseService; app = create_app('development'); app.app_context().push(); db_service = DatabaseService(db.session); db_service.initialize_database()"

# 启动应用
python app.py
```

### 3️⃣ 访问应用
打开浏览器访问: **http://localhost:5001**

**测试账号:**
- 管理员: `admin@dev.com`
- 普通用户: `user@dev.com`

## 📁 项目结构

```
EquityCompass/
├── 📄 README.md                 # 项目说明 (本文件)
├── 📄 PROJECT_STRUCTURE.md      # 🗂️ 详细结构说明
├── 📄 prd.md                    # 📋 产品需求文档
├── 📁 backend/                  # 🐍 Flask后端应用
│   ├── 📄 app.py               # 应用入口
│   ├── 📁 app/                 # 主应用代码
│   ├── 📁 tests/               # 🧪 测试代码
│   └── 📁 venv/                # Python虚拟环境
├── 📁 docs/                     # 📚 项目文档
├── 📁 data/                     # 📊 数据存储
├── 📁 configs/                  # ⚙️ 配置文件
├── 📁 docker/                   # 🐳 Docker配置
└── 📁 scripts/                  # 🔧 部署脚本
```

## 🎯 核心功能

### 👤 用户系统 ✅
- [x] 邮箱验证码登录
- [x] JWT Token认证
- [x] 用户资料管理
- [x] 权限控制系统

### 📊 股票数据 ✅
- [x] 美股/港股TOP100股票池
- [x] 股票搜索和筛选
- [x] 关注列表管理 (最多20支)
- [x] 自定义股票添加

### 🤖 AI分析 🚧
- [ ] 多LLM集成 (Gemini/ChatGPT/Qwen)
- [ ] 智能分析报告生成
- [ ] 定时分析任务
- [ ] 报告管理和导出

### 💳 订阅系统 📅
- [ ] 多层级订阅计划
- [ ] 支付网关集成
- [ ] 使用额度管理
- [ ] 账单和发票

## 🧪 测试状态

| 模块 | 测试文件 | 通过率 | 状态 |
|------|----------|--------|------|
| 数据层 | test_data_layer.py | 100% (59/59) | ✅ |
| 用户系统 | test_user_system.py | 90.5% (19/21) | ✅ |
| API接口 | test_detailed_api.py | 100% | ✅ |
| 前端界面 | test_frontend_simple.py | 100% (39/39) | ✅ |

**运行测试:**
```bash
cd backend
python tests/backend/test_data_layer.py
python tests/frontend/test_frontend_simple.py
```

## 🛠️ 技术架构

### 🐍 后端技术栈
- **框架**: Flask + Jinja2
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT + 邮箱验证码
- **任务队列**: Celery + Redis
- **邮件服务**: SMTP (支持多提供商)

### 🎨 前端技术栈
- **模板引擎**: Jinja2
- **样式框架**: Bootstrap 5
- **图标库**: Font Awesome 6
- **JavaScript**: 原生ES6+ (无框架依赖)

### 🏗️ 架构设计
- **分层架构**: API → Service → Repository → Model
- **模块化设计**: 认证、数据、邮件等独立服务
- **配置分离**: 开发/测试/生产环境配置
- **容器化**: Docker + Docker Compose支持

## 📖 开发文档

- [📋 产品需求文档](./prd.md)
- [🗂️ 项目结构说明](./PROJECT_STRUCTURE.md)
- [🏗️ 系统架构设计](./docs/architecture/)
- [🌐 API接口文档](./docs/api/)
- [🗃️ 数据库设计](./docs/database/)
- [📝 开发日志](./docs/development-log.md)

## 🤝 参与贡献

1. Fork 项目
2. 创建特性分支: `git checkout -b feature/AmazingFeature`
3. 提交变更: `git commit -m 'Add some AmazingFeature'`
4. 推送分支: `git push origin feature/AmazingFeature`
5. 开启Pull Request

## 📞 联系我们

- 📧 邮箱: contact@equitycompass.com
- 💬 讨论: [GitHub Discussions](https://github.com/yourusername/EquityCompass/discussions)
- 🐛 问题反馈: [GitHub Issues](https://github.com/yourusername/EquityCompass/issues)

## 📜 开源协议

本项目基于 [MIT License](LICENSE) 开源协议。

---

⭐ **如果这个项目对您有帮助，请给我们一个Star！** ⭐