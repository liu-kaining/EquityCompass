# 智策股析 (EquityCompass)

一个基于AI的智能股票分析平台，提供专业的股票分析报告和投资建议。

## 🚀 功能特性

### 核心功能
- **AI智能分析**: 支持多种AI模型（DeepSeek、通义千问、OpenAI、Gemini）
- **股票关注列表**: 用户可以关注感兴趣的股票，最多20支
- **批量分析**: 支持单支股票和批量股票分析
- **分析报告**: 生成专业的股票分析报告，包含基本面和技术面分析
- **报告管理**: 查看、下载、导出分析报告
- **任务管理**: 实时查看分析任务状态，支持暂停、删除、重试操作

### 用户管理
- **用户注册/登录**: 支持邮箱注册和登录
- **邮箱验证**: 注册时发送验证码到邮箱
- **管理员功能**: 管理员可以查看全局统计和管理用户

### 数据统计
- **全局统计**: 总报告数、浏览次数、下载次数等
- **每日统计**: 按日期统计分析趋势
- **热门报告**: 显示最受欢迎的分析报告
- **数据清理**: 管理员可以一键清空所有统计数据

### 技术特性
- **响应式设计**: 支持桌面和移动端访问
- **实时更新**: 任务状态实时更新
- **PDF导出**: 支持将分析报告导出为PDF格式
- **批量导出**: 支持批量导出多个报告为ZIP文件
- **访客模式**: 无需登录即可查看公开报告

## 🛠️ 技术栈

### 后端
- **框架**: Flask 2.3.3
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.0+
- **认证**: Flask-Login + JWT
- **邮件**: Flask-Mail
- **AI集成**: OpenAI, Google Gemini, 阿里云通义千问, DeepSeek

### 前端
- **框架**: Bootstrap 5 + jQuery
- **图标**: Font Awesome
- **图表**: Chart.js
- **PDF生成**: Playwright + ReportLab

### 部署
- **容器化**: Docker + Docker Compose
- **Web服务器**: Gunicorn
- **反向代理**: Nginx (生产环境)

## 📦 本地部署

### 环境要求
- Python 3.8+
- Node.js 16+ (用于Playwright)
- Git

### 1. 克隆项目
```bash
git clone https://github.com/your-username/EquityCompass.git
cd EquityCompass
```

### 2. 后端设置
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium

# 复制环境变量文件
cp env.example .env

# 编辑环境变量
nano .env  # 或使用其他编辑器
```

### 3. 配置环境变量
编辑 `.env` 文件，配置以下关键参数：

```env
# 基本配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# AI模型配置（至少配置一个）
DEEPSEEK_API_KEY=your-deepseek-api-key
QWEN_API_KEY=your-qwen-api-key
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# 邮件配置（可选）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SEND_EMAIL=True

# 管理员配置
ADMIN_EMAIL=admin@equitycompass.com
```

### 4. 初始化数据库
```bash
# 初始化数据库
python scripts/init_db.py

# 创建测试数据（可选）
python create_test_statistics_data.py
```

### 5. 启动应用
```bash
# 开发模式
python run.py

# 或使用脚本
./scripts/start_dev.sh
```

应用将在 http://localhost:5002 启动

### 6. 访问应用
- 主页: http://localhost:5002
- 管理员登录: 使用 `ADMIN_EMAIL` 配置的邮箱，密码为 `admin123`

## 🐳 Docker部署

### 1. 使用Docker Compose（推荐）
```bash
# 复制环境变量文件
cp backend/env.example .env

# 编辑环境变量
nano .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 2. 手动Docker部署
```bash
# 构建镜像
docker build -t equitycompass .

# 运行容器
docker run -d \
  --name equitycompass \
  -p 5002:5002 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  equitycompass
```

### 3. 生产环境部署
```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d
```

## 📁 项目结构

```
EquityCompass/
├── backend/                 # 后端代码
│   ├── app/                # Flask应用
│   │   ├── api/            # API接口
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── templates/      # HTML模板
│   │   ├── static/         # 静态文件
│   │   └── views/          # 视图函数
│   ├── data/               # 数据文件
│   ├── tests/              # 测试文件
│   ├── scripts/            # 脚本文件
│   ├── requirements.txt    # Python依赖
│   └── run.py             # 启动文件
├── docs/                   # 文档
├── scripts/                # 部署脚本
├── docker-compose.yml      # Docker配置
├── Dockerfile             # Docker镜像
└── README.md              # 项目说明
```

## 🔧 开发指南

### 运行测试
```bash
cd backend
python -m pytest tests/ -v
```

### 代码格式化
```bash
# 格式化代码
black app/

# 检查代码质量
flake8 app/
```

### 数据库迁移
```bash
# 创建迁移
flask db migrate -m "描述"

# 应用迁移
flask db upgrade
```

## 🔑 API文档

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/verify` - 邮箱验证

### 分析接口
- `POST /api/analysis/single` - 单支股票分析
- `POST /api/analysis/batch` - 批量股票分析
- `GET /api/analysis/tasks` - 获取任务列表
- `POST /api/analysis/tasks/{task_id}/pause` - 暂停任务
- `DELETE /api/analysis/tasks/{task_id}` - 删除任务

### 报告接口
- `GET /reports/` - 报告列表
- `GET /reports/{stock_code}` - 报告详情
- `GET /reports/{stock_code}/export-pdf` - 导出PDF
- `POST /reports/batch-export` - 批量导出

### 统计接口
- `GET /api/report-statistics/global-stats` - 全局统计
- `GET /api/report-statistics/daily-stats` - 每日统计
- `GET /api/report-statistics/popular` - 热门报告
- `POST /api/report-statistics/clear-all` - 清空统计（管理员）

## 🚨 故障排除

### 常见问题

1. **AI分析失败**
   - 检查API密钥是否正确配置
   - 确认网络连接正常
   - 查看应用日志获取详细错误信息

2. **邮件发送失败**
   - 检查SMTP配置
   - 确认邮箱密码为应用专用密码
   - 检查防火墙设置

3. **PDF导出失败**
   - 确认Playwright已正确安装
   - 检查浏览器依赖
   - 查看系统资源使用情况

4. **数据库连接问题**
   - 检查数据库文件权限
   - 确认数据库路径正确
   - 查看数据库日志

### 日志查看
```bash
# 查看应用日志
tail -f backend/app.log

# 查看Docker日志
docker-compose logs -f
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目链接: [https://github.com/your-username/EquityCompass](https://github.com/your-username/EquityCompass)
- 问题反馈: [Issues](https://github.com/your-username/EquityCompass/issues)

## 🙏 致谢

感谢以下开源项目的支持：
- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [Font Awesome](https://fontawesome.com/)
- [Playwright](https://playwright.dev/)

---

**注意**: 这是一个演示项目，请在生产环境中使用前进行充分的安全配置和测试。