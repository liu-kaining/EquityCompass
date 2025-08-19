# 智策股析 - 项目结构说明

## 📁 项目整体结构

```
EquityCompass/
├── 📄 README.md                 # 项目说明文档
├── 📄 prd.md                    # 产品需求文档
├── 📄 PROJECT_STRUCTURE.md      # 项目结构说明（本文件）
├── 📁 docs/                     # 📚 项目文档
├── 📁 backend/                  # 🐍 Python Flask后端
├── 📁 configs/                  # ⚙️ 全局配置文件
├── 📁 data/                     # 📊 数据存储目录
├── 📁 docker/                   # 🐳 Docker配置
└── 📁 scripts/                  # 🔧 项目脚本
```

## 🐍 Backend 后端结构

```
backend/
├── 📄 app.py                    # Flask应用入口
├── 📄 requirements.txt          # Python依赖
├── 📄 env.example              # 环境变量示例
├── 📁 app/                      # 🏗️ 主应用目录
│   ├── 📄 __init__.py          # Flask应用工厂
│   ├── 📄 config.py            # 应用配置
│   ├── 📁 api/                 # 🌐 RESTful API接口
│   │   ├── 📄 auth_api.py      # 用户认证API
│   │   ├── 📄 stocks_api.py    # 股票相关API  
│   │   ├── 📄 health.py        # 健康检查API
│   │   └── 📄 ...              # 其他API模块
│   ├── 📁 views/               # 🎨 Web页面视图
│   │   ├── 📄 auth.py          # 认证页面
│   │   ├── 📄 dashboard.py     # 仪表板页面
│   │   ├── 📄 stocks.py        # 股票页面
│   │   └── 📄 ...              # 其他页面视图
│   ├── 📁 models/              # 🗃️ 数据模型
│   │   ├── 📄 user.py          # 用户模型
│   │   ├── 📄 stock.py         # 股票模型
│   │   └── 📄 ...              # 其他数据模型
│   ├── 📁 repositories/        # 🏪 数据访问层
│   │   ├── 📄 base.py          # 基础Repository
│   │   ├── 📄 user_repository.py
│   │   └── 📄 ...              # 其他Repository
│   ├── 📁 services/            # 🔧 业务逻辑层
│   │   ├── 📁 auth/            # 认证服务
│   │   ├── 📁 data/            # 数据服务
│   │   └── 📁 email/           # 邮件服务
│   ├── 📁 templates/           # 🎨 HTML模板
│   │   ├── 📄 base.html        # 基础模板
│   │   ├── 📁 auth/            # 认证页面模板
│   │   ├── 📁 dashboard/       # 仪表板模板
│   │   └── 📁 ...              # 其他页面模板
│   ├── 📁 static/              # 🎨 静态资源
│   │   ├── 📁 css/             # 样式文件
│   │   ├── 📁 js/              # JavaScript文件
│   │   └── 📁 images/          # 图片资源
│   ├── 📁 tasks/               # ⚙️ Celery任务
│   └── 📁 utils/               # 🛠️ 工具函数
├── 📁 tests/                   # 🧪 测试代码
│   ├── 📁 backend/             # 后端测试
│   ├── 📁 frontend/            # 前端测试
│   └── 📁 integration/         # 集成测试
├── 📁 logs/                    # 📝 日志文件
├── 📁 instance/                # 🗄️ 实例数据（SQLite等）
├── 📁 migrations/              # 🔄 数据库迁移
└── 📁 venv/                    # 🐍 Python虚拟环境
```

## 📚 文档结构

```
docs/
├── 📄 README.md                # 文档导航
├── 📁 architecture/            # 🏗️ 系统架构设计
├── 📁 api/                     # 🌐 API接口文档
├── 📁 database/                # 🗃️ 数据库设计
├── 📁 deployment/              # 🚀 部署文档
├── 📁 business-flows/          # 📊 业务流程
└── 📄 development-log.md       # 📝 开发日志
```

## 🗃️ 数据存储结构

```
data/
├── 📁 reports/                 # 📊 AI分析报告
│   ├── 📁 2025/               # 按年份组织
│   │   ├── 📁 01/             # 按月份组织
│   │   │   ├── 📁 20/         # 按日期组织
│   │   │   │   ├── 📄 AAPL_analysis.json
│   │   │   │   └── 📄 ...
├── 📁 exports/                 # 📤 导出文件
└── 📁 logs/                    # 📝 应用日志
```

## 🔧 配置文件结构

```
configs/
├── 📄 development.yml          # 开发环境配置
├── 📄 production.yml           # 生产环境配置
└── 📄 testing.yml              # 测试环境配置
```

## 🐳 Docker 结构

```
docker/
├── 📄 Dockerfile.backend       # 后端Docker文件
├── 📄 docker-compose.yml       # Docker编排文件
├── 📄 docker-compose.prod.yml  # 生产环境编排
└── 📁 nginx/                   # Nginx配置
```

## 🔧 脚本结构

```
scripts/
├── 📄 setup_backend.sh         # 后端环境搭建
├── 📄 start_dev.sh            # 开发环境启动
├── 📄 deploy.sh                # 部署脚本
└── 📄 backup.sh                # 数据备份脚本
```

## 🗂️ 核心模块说明

### 🏗️ 分层架构

1. **API层** (`app/api/`) - RESTful API接口
2. **View层** (`app/views/`) - Web页面控制器
3. **Service层** (`app/services/`) - 业务逻辑处理
4. **Repository层** (`app/repositories/`) - 数据访问抽象
5. **Model层** (`app/models/`) - 数据模型定义

### 🔄 数据流向

```
Web请求 → View层 → Service层 → Repository层 → Model层 → 数据库
API请求 → API层 → Service层 → Repository层 → Model层 → 数据库
```

### 🧪 测试策略

- **单元测试**: 测试单个函数/类
- **集成测试**: 测试模块间交互
- **API测试**: 测试RESTful接口
- **前端测试**: 测试用户界面交互

## 📋 开发规范

### 📁 文件命名
- Python文件: `snake_case.py`
- 类名: `PascalCase`
- 函数名: `snake_case`
- 常量: `UPPER_CASE`

### 📝 代码组织
- 每个模块单一职责
- 接口和实现分离
- 配置与代码分离
- 测试代码完整覆盖

### 🔧 环境管理
- 开发环境: SQLite + 内存缓存
- 测试环境: 独立测试数据库
- 生产环境: PostgreSQL + Redis

## 🚀 快速开始

1. **环境搭建**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **数据库初始化**
   ```bash
   python -c "from app import create_app, db; from app.services.data.database_service import DatabaseService; app = create_app('development'); app.app_context().push(); db_service = DatabaseService(db.session); db_service.initialize_database()"
   ```

3. **启动应用**
   ```bash
   python app.py
   ```

4. **运行测试**
   ```bash
   python tests/backend/test_data_layer.py
   python tests/frontend/test_frontend_simple.py
   ```

## 📝 维护说明

- 定期更新依赖: `pip list --outdated`
- 数据库备份: 参考 `scripts/backup.sh`
- 日志清理: 定期清理 `logs/` 目录
- 测试覆盖: 保持测试覆盖率 > 80%

---

*最后更新: 2025-08-20*
*维护者: 智策股析开发团队*
