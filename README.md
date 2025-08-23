# EquityCompass - AI驱动的股票分析平台

## 项目简介

EquityCompass 是一个基于人工智能的股票分析平台，集成了多个先进的AI模型（Gemini、Qwen、DeepSeek），为用户提供专业的股票基本面和技术面分析报告。平台采用现代化的Web界面，支持实时分析、报告管理、PDF导出等功能。

## 🚀 核心功能

### 1. 智能股票分析
- **多AI模型支持**: 集成Gemini、Qwen、DeepSeek三大AI模型
- **双分析模式**: 基本面分析 + 技术面分析
- **实时分析**: 支持单个股票和批量分析
- **异步处理**: 后台任务处理，支持进度跟踪

### 2. 报告管理系统
- **报告存储**: 自动保存所有分析报告
- **历史查看**: 查看同一公司的历史分析报告
- **报告详情**: 完整的报告内容展示
- **分页浏览**: 支持大量报告的分页显示

### 3. 导出功能
- **PDF导出**: 单个报告导出为PDF，保持网页样式
- **批量导出**: 多选报告批量导出为ZIP压缩包
- **中文支持**: 完美支持中文显示和排版

### 4. 用户管理
- **每日限制**: 普通用户每日10次分析限制
- **管理员权限**: 管理员无限制使用
- **使用统计**: 实时显示当日使用情况

### 5. 股票管理
- **内置股票池**: 包含主流股票数据
- **自定义股票**: 支持添加自定义股票
- **股票分类**: 内置股票vs自定义股票区分

### 6. 任务管理
- **任务队列**: 异步任务处理系统
- **状态跟踪**: 实时任务状态更新
- **重试机制**: 自动重试失败任务（最多5次）
- **手动重试**: 支持手动重试失败任务

## 🛠️ 技术架构

### 后端技术栈
- **框架**: Flask (Python)
- **数据库**: SQLite + SQLAlchemy ORM
- **AI集成**: Google Gemini、阿里云Qwen、DeepSeek API
- **PDF生成**: Playwright + Markdown
- **异步处理**: Python threading
- **日志系统**: Python logging

### 前端技术栈
- **模板引擎**: Jinja2
- **样式框架**: Bootstrap 5
- **JavaScript**: 原生JS + jQuery
- **响应式设计**: 移动端友好

### 核心特性
- **时区处理**: 统一使用北京时间(UTC+8)
- **错误处理**: 完善的异常处理机制
- **日志记录**: 详细的LLM调用日志
- **模块化设计**: 清晰的服务层架构

## 📦 快速开始

### 方式一：Docker部署（推荐）

#### 环境要求
- Docker
- Docker Compose

#### 部署步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass
```

2. **配置环境变量**
```bash
cp backend/env.example .env
# 编辑 .env 文件，配置必要的API密钥
```

3. **使用Docker Compose启动**
```bash
docker-compose up -d
```

4. **初始化数据库和导入数据**
```bash
# 进入容器
docker exec -it equitycompass-app bash

# 初始化数据库
python app.py init-db

# 导入股票数据
python scripts/import_stocks.py

# 退出容器
exit
```

5. **访问应用**
打开浏览器访问: http://localhost:5001

#### Docker命令参考
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建镜像
docker-compose build --no-cache

# 查看容器状态
docker-compose ps
```

### 方式二：本地开发环境

#### 环境要求
- Python 3.9+
- pip
- Git

#### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass
```

2. **创建虚拟环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
python app.py init-db
```

5. **导入股票数据**
```bash
python scripts/import_stocks.py
```

6. **启动应用**
```bash
python app.py
```

7. **访问应用**
打开浏览器访问: http://localhost:5001

### 环境配置

复制环境变量模板并配置：
```bash
cp env.example .env
```

主要配置项：
- `FLASK_SECRET_KEY`: Flask密钥
- `GEMINI_API_KEY`: Google Gemini API密钥
- `QWEN_API_KEY`: 阿里云Qwen API密钥
- `DEEPSEEK_API_KEY`: DeepSeek API密钥

## 📁 项目结构

```
EquityCompass/
├── backend/                 # 后端应用
│   ├── app/                # 应用核心
│   │   ├── models/         # 数据模型
│   │   ├── views/          # 视图控制器
│   │   ├── services/       # 业务服务
│   │   ├── templates/      # 前端模板
│   │   └── static/         # 静态资源
│   ├── data/               # 数据存储
│   │   ├── reports/        # 分析报告
│   │   ├── tasks/          # 任务数据
│   │   └── usage/          # 使用统计
│   ├── scripts/            # 脚本工具
│   ├── tests/              # 测试文件
│   └── requirements.txt    # Python依赖
├── docs/                   # 文档
├── configs/                # 配置文件
└── README.md              # 项目说明
```

## 🐳 Docker部署

### 生产环境部署

#### 1. 环境准备
确保服务器已安装Docker和Docker Compose：
```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 部署配置
```bash
# 克隆项目
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass

# 配置环境变量
cp backend/env.example .env
nano .env  # 编辑配置文件
```

#### 3. 启动服务
```bash
# 构建并启动
docker-compose up -d --build

# 查看启动状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 4. 数据初始化
```bash
# 进入容器执行初始化
docker exec -it equitycompass-app python app.py init-db
docker exec -it equitycompass-app python scripts/import_stocks.py
```

### 容器管理

#### 常用命令
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f equitycompass

# 进入容器
docker exec -it equitycompass-app bash

# 更新代码后重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 数据持久化
- 应用数据存储在Docker卷中：`equitycompass_data`
- 日志文件存储在Docker卷中：`equitycompass_logs`
- 数据库文件持久化在容器中

#### 健康检查
容器内置健康检查，可通过以下命令查看：
```bash
docker inspect equitycompass-app | grep Health -A 10
```

## 🔧 开发指南

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型提示
- 编写详细的文档字符串
- 保持代码模块化

### 测试
运行全面测试：
```bash
python scripts/run_all_tests.py
```

### 数据库管理
```bash
# 初始化数据库
python app.py init-db

# 填充初始数据
python app.py seed-db

# 重置数据库（危险操作）
python app.py reset-db
```

## 📊 功能演示

### 1. 股票分析
- 选择股票和AI模型
- 选择分析类型（基本面/技术面）
- 提交分析请求
- 查看实时进度
- 获取分析报告

### 2. 报告管理
- 浏览所有分析报告
- 查看报告详情
- 查看历史报告
- 导出PDF报告
- 批量导出报告

### 3. 任务管理
- 查看所有任务状态
- 监控任务进度
- 重试失败任务
- 查看任务详情

## 🔒 安全特性

- 用户认证和授权
- API密钥安全存储
- 输入验证和过滤
- 错误信息保护
- 日志安全记录

## 📈 性能优化

- 异步任务处理
- 数据库查询优化
- 静态资源缓存
- 分页加载
- 内存管理

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 更新日志

### v1.0.0 (2025-08-23)
- ✅ 完成核心分析功能
- ✅ 实现PDF导出功能
- ✅ 添加批量导出功能
- ✅ 优化UI/UX设计
- ✅ 完善异步任务系统
- ✅ 实现分页功能
- ✅ 修复时区问题
- ✅ 添加用户权限控制
- ✅ 完善日志系统

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目链接: [https://github.com/your-username/EquityCompass](https://github.com/your-username/EquityCompass)

## 🙏 致谢

感谢以下开源项目和服务：
- Flask - Web框架
- Bootstrap - UI框架
- Google Gemini - AI模型
- 阿里云Qwen - AI模型
- DeepSeek - AI模型
- Playwright - PDF生成

---

**注意**: 本平台生成的分析报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。