# 智策股析 - 每日股价分析与决策平台

[![前端](https://img.shields.io/badge/前端-React%2018-blue)](https://reactjs.org/)
[![后端](https://img.shields.io/badge/后端-Flask-green)](https://flask.palletsprojects.com/)
[![数据库](https://img.shields.io/badge/数据库-SQLite%2FPostgreSQL-orange)](https://www.sqlite.org/)
[![任务队列](https://img.shields.io/badge/任务队列-Celery%2BRedis-red)](https://docs.celeryproject.org/)

> 🤖 通过AI驱动的每日股票分析，为个人投资者提供专业的投资决策支持

## ✨ 核心特性

- 🔐 **无密码认证** - 邮箱验证码快速登录
- 📊 **个性化分析** - 自定义关注最多20支股票
- 🤖 **多模型支持** - 集成Gemini、Qwen、ChatGPT等LLM
- ⚡ **异步处理** - Celery任务队列保证响应速度
- 💰 **试用付费** - 新用户免费试用，灵活付费模式
- 📧 **邮件订阅** - 每日分析摘要自动推送
- 📱 **响应式设计** - 完美适配桌面和移动设备

## 🏗️ 项目结构

```
EquityCompass/
├── backend/                 # Flask后端
│   ├── app/                # 应用主目录
│   │   ├── api/           # API路由
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务
│   │   ├── tasks/         # Celery任务
│   │   └── utils/         # 工具函数
│   ├── requirements.txt   # Python依赖
│   └── app.py             # 应用入口
├── frontend/               # React前端
│   ├── src/               # 源码目录
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   ├── contexts/      # React Context
│   │   ├── styles/        # 样式文件
│   │   └── types/         # TypeScript类型
│   └── package.json       # Node.js依赖
├── data/                   # 数据存储
│   ├── reports/           # 分析报告(JSON)
│   ├── exports/           # 导出文件
│   └── logs/              # 日志文件
├── docs/                   # 技术文档
├── scripts/                # 启动脚本
└── configs/                # 配置文件
```

## 🚀 快速开始

### 环境要求

- **Python 3.8+**
- **Node.js 16+**
- **Redis 6+**

### 1. 克隆项目

```bash
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass
```

### 2. 后端设置

```bash
# 运行后端环境设置脚本
./scripts/setup_backend.sh

# 或手动设置
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env  # 编辑环境变量
```

### 3. 前端设置

```bash
# 运行前端环境设置脚本
./scripts/setup_frontend.sh

# 或手动设置
cd frontend
npm install
cp env.example .env  # 编辑环境变量
```

### 4. 启动开发环境

```bash
# 一键启动所有服务
./scripts/start_dev.sh

# 或分别启动
# 终端1: 启动Redis
redis-server

# 终端2: 启动后端
cd backend && source venv/bin/activate && python app.py

# 终端3: 启动前端
cd frontend && npm start
```

### 5. 访问应用

- 🌐 **前端**: http://localhost:3000
- 🔧 **后端API**: http://localhost:5000
- 📊 **健康检查**: http://localhost:5000/api/health

## 📖 API文档

完整的API文档请查看: [docs/api/api-design.md](docs/api/api-design.md)

### 主要API端点

```bash
# 认证相关
POST /api/auth/send-code      # 发送验证码
POST /api/auth/verify-code    # 验证登录
POST /api/auth/logout         # 登出

# 股票相关
GET  /api/stocks              # 获取股票列表
POST /api/stocks              # 添加自定义股票
GET  /api/watchlist           # 获取关注列表
POST /api/watchlist           # 添加到关注列表

# 分析相关
POST /api/analysis/trigger    # 触发分析任务
GET  /api/analysis/status     # 获取任务状态
GET  /api/reports             # 获取报告列表
GET  /api/reports/{id}        # 获取报告详情
```

## 🔧 开发指南

### 代码规范

- **后端**: 遵循PEP 8规范，使用black格式化
- **前端**: 遵循ESLint + Prettier规范
- **提交**: 使用约定式提交格式

### 运行测试

```bash
# 后端测试
cd backend
python -m pytest

# 前端测试
cd frontend
npm test
```

### 数据库操作

```bash
# 初始化数据库
cd backend && source venv/bin/activate
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# 数据库迁移
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📚 技术文档

详细的技术文档位于 `docs/` 目录：

- [📋 系统架构总览](docs/architecture/01-system-overview.md)
- [🏗️ 子系统设计](docs/architecture/02-subsystems-design.md)
- [🗄️ 数据库设计](docs/database/database-design.md)
- [🔌 API接口设计](docs/api/api-design.md)
- [🚀 部署架构](docs/deployment/deployment-architecture.md)
- [🔄 业务流程](docs/business-flows/core-business-flows.md)

## 🎯 开发路线图

### 🚧 第一阶段 (MVP) - 当前状态
- [x] 项目基础框架搭建
- [x] 用户认证系统设计
- [x] 数据库模型设计
- [x] API接口设计
- [ ] 前端基础页面实现
- [ ] 后端API实现
- [ ] 基础功能测试

### 🔜 第二阶段 (核心功能)
- [ ] LLM集成和分析引擎
- [ ] Celery异步任务系统
- [ ] 股票数据获取
- [ ] 报告生成和存储
- [ ] 用户关注列表管理

### 🎨 第三阶段 (完善体验)
- [ ] 支付系统集成
- [ ] 邮件订阅功能
- [ ] 报告导出功能
- [ ] UI/UX优化
- [ ] 移动端适配

### 🚀 第四阶段 (生产部署)
- [ ] 性能优化
- [ ] 安全加固
- [ ] 监控告警
- [ ] 生产环境部署

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系我们

- 📧 Email: contact@equitycompass.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/EquityCompass/issues)
- 📖 文档: [项目文档](docs/README.md)

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！