# 智策股析 (EquityCompass)

> AI驱动的智能股票分析平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 项目简介

智策股析是一个基于AI的智能股票分析平台，为用户提供专业的股票基本面和技术面分析报告。平台支持多用户系统，具备完整的权限管理功能，让用户能够轻松管理投资组合并获取AI驱动的投资洞察。

### ✨ 核心功能

- **🤖 AI智能分析** - 支持多种AI模型（DeepSeek、OpenAI、Qwen、Gemini等）
- **⚙️ AI配置管理** - 动态管理AI模型配置，支持API密钥管理和连接测试
- **📝 提示词管理** - 提示词版本管理，支持自定义和版本控制
- **📊 股票池管理** - 覆盖美股和港股市场，支持自定义股票添加
- **👥 多用户系统** - 完整的用户注册、登录和权限管理
- **📈 关注列表** - 个性化股票关注和监控
- **📋 任务管理** - 批量分析任务创建和状态跟踪，支持任务重试
- **📄 报告生成** - 专业的PDF报告导出功能
- **🔐 权限控制** - 三级权限体系（超级管理员、网站管理员、普通用户）
- **📊 数据统计** - 管理员专用的数据统计和分析功能
- **🔄 任务重试** - 智能任务重试机制，自动重新调用AI模型

## 🏗️ 系统架构

### 技术栈

- **后端框架**: Flask 2.3+
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy
- **认证**: JWT + Session
- **前端**: Jinja2模板 + Bootstrap 5
- **AI集成**: DeepSeek、OpenAI、Qwen、Gemini
- **PDF生成**: Playwright
- **部署**: Docker + Docker Compose

### 架构设计

```
EquityCompass/
├── backend/                 # 后端应用
│   ├── app/
│   │   ├── api/            # API接口层
│   │   ├── models/         # 数据模型层
│   │   ├── repositories/   # 数据访问层
│   │   ├── services/       # 业务逻辑层
│   │   ├── views/          # 视图控制层
│   │   ├── templates/      # 前端模板
│   │   └── utils/          # 工具函数
│   ├── data/               # 数据文件
│   ├── scripts/            # 管理脚本
│   └── tests/              # 测试文件
├── docs/                   # 项目文档
└── scripts/                # 部署脚本
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+ (用于前端构建)
- Docker & Docker Compose (可选)

### 本地开发

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
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp env.example .env
   # 编辑 .env 文件，配置必要的环境变量
   ```

5. **初始化数据库**
   ```bash
   python scripts/init_db.py
   python scripts/import_stocks.py
   python scripts/setup_admin_user.py
   python scripts/init_ai_configs.py
   ```

6. **启动应用**
   ```bash
   python run.py
   ```

7. **访问应用**
   - 应用地址: http://localhost:5002
   - 管理员登录: admin / admin123456

### Docker部署

1. **构建并启动**
   ```bash
   docker-compose up -d
   ```

2. **初始化数据**
   ```bash
   docker-compose exec backend python scripts/init_db.py
   docker-compose exec backend python scripts/import_stocks.py
   docker-compose exec backend python scripts/setup_admin_user.py
   docker-compose exec backend python scripts/init_ai_configs.py
   ```

## ⚙️ 配置说明

### 环境变量配置

创建 `.env` 文件并配置以下变量：

```bash
# 基本配置
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# 数据库配置
DATABASE_URL=sqlite:///dev.db

# AI模型配置
DEEPSEEK_API_KEY=your-deepseek-api-key
OPENAI_API_KEY=your-openai-api-key
QWEN_API_KEY=your-qwen-api-key
GEMINI_API_KEY=your-gemini-api-key

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@equitycompass.com
ADMIN_PASSWORD=admin123456
ADMIN_NICKNAME=系统管理员

# 邮件配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SEND_EMAIL=True
```

### 管理员配置

系统支持通过环境变量配置管理员账户：

- `ADMIN_USERNAME`: 管理员用户名
- `ADMIN_EMAIL`: 管理员邮箱
- `ADMIN_PASSWORD`: 管理员密码
- `ADMIN_NICKNAME`: 管理员昵称

## 👥 用户权限系统

### 权限等级

1. **SUPER_ADMIN (超级管理员)**
   - 完整的系统管理权限
   - 用户管理（增删改查、角色管理、状态管理）
   - 所有报告查看和下载
   - 系统配置管理

2. **SITE_ADMIN (网站管理员)**
   - 除用户管理外的所有管理权限
   - 报告统计查看
   - 所有报告查看和下载

3. **USER (普通用户)**
   - 个人数据管理
   - 关注股票管理
   - 个人报告查看和下载
   - 任务创建和管理

### 权限控制

系统使用装饰器实现细粒度的权限控制：

```python
@login_required          # 需要登录
@admin_required          # 需要管理员权限
@super_admin_required    # 需要超级管理员权限
@user_management_required # 需要用户管理权限
@statistics_access_required # 需要统计页面访问权限
```

## 📊 功能模块

### 1. 用户管理

- **用户注册**: 支持用户名密码注册，包含完整的输入验证
- **用户登录**: 支持用户名密码登录和邮箱验证码登录
- **权限管理**: 基于角色的权限控制系统
- **用户资料**: 个人信息管理和更新

### 2. 股票管理

- **股票池**: 预置美股和港股数据，支持搜索和筛选
- **关注列表**: 个人股票关注管理，最多20只股票
- **自定义股票**: 支持添加自定义股票到股票池
- **股票详情**: 详细的股票信息展示

### 3. 分析任务

- **任务创建**: 支持单只股票和批量股票分析
- **任务管理**: 任务状态跟踪和历史记录
- **进度监控**: 实时任务进度显示
- **结果查看**: 分析结果即时查看
- **任务重试**: 智能重试机制，失败任务自动重新调用AI模型
- **后台执行**: 异步任务执行，不阻塞用户操作

### 4. 报告系统

- **报告生成**: AI驱动的专业分析报告
- **报告查看**: 支持多种格式的报告展示
- **报告下载**: PDF格式报告导出
- **批量导出**: 支持多报告批量下载
- **历史报告**: 同一股票的历史分析记录

### 5. AI配置管理

- **模型配置**: 动态管理AI模型配置，支持多种提供商
- **API密钥管理**: 安全的API密钥存储和管理
- **连接测试**: 实时测试AI模型连接状态
- **使用统计**: AI模型使用情况统计和分析

### 6. 提示词管理

- **提示词版本**: 支持提示词版本管理和历史记录
- **自定义提示词**: 创建和编辑自定义分析提示词
- **版本控制**: 保留多个版本，支持版本切换
- **使用统计**: 提示词使用频率和效果统计

### 7. 管理员功能

- **用户管理**: 用户信息查看、角色管理、状态控制
- **数据统计**: 系统使用统计和数据分析
- **报告管理**: 所有用户报告的查看和管理
- **系统监控**: 系统运行状态监控

## 🔧 API接口

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/refresh` - 刷新Token
- `GET /api/auth/profile` - 获取用户资料
- `PUT /api/auth/profile` - 更新用户资料

### 股票接口

- `GET /api/stocks/` - 获取股票列表
- `GET /api/stocks/<code>` - 获取股票详情
- `POST /api/stocks/watchlist` - 添加关注
- `DELETE /api/stocks/watchlist/<code>` - 取消关注

### 分析接口

- `POST /api/analysis/analyze` - 创建分析任务
- `GET /api/analysis/tasks` - 获取任务列表
- `GET /api/analysis/task-status/<task_id>` - 获取任务状态
- `POST /api/analysis/retry-task/<task_id>` - 重试失败任务
- `POST /api/analysis/pause-task/<task_id>` - 暂停任务
- `POST /api/analysis/resume-task/<task_id>` - 恢复任务
- `DELETE /api/analysis/delete-task/<task_id>` - 删除任务
- `GET /api/analysis/reports` - 获取报告列表
- `GET /api/analysis/reports/<stock_code>` - 获取报告详情

### AI配置接口

- `GET /admin/ai-configs` - AI配置管理页面
- `GET /api/ai-configs/` - 获取所有AI配置
- `POST /api/ai-configs/` - 创建AI配置
- `PUT /api/ai-configs/<id>` - 更新AI配置
- `DELETE /api/ai-configs/<id>` - 删除AI配置
- `POST /api/ai-configs/<id>/test` - 测试AI配置连接

### 提示词管理接口

- `GET /admin/prompts` - 提示词管理页面
- `GET /api/prompts/` - 获取所有提示词
- `GET /api/prompts/type/<type>` - 根据类型获取提示词
- `POST /api/prompts/` - 创建提示词
- `PUT /api/prompts/<id>` - 更新提示词
- `DELETE /api/prompts/<id>` - 删除提示词

### 管理员接口

- `GET /admin/users` - 用户管理页面
- `PUT /admin/api/users/<id>/role` - 更新用户角色
- `PUT /admin/api/users/<id>/status` - 更新用户状态
- `GET /admin/api/users/<id>/details` - 获取用户详情

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python scripts/run_all_tests.py

# 运行特定测试
python -m pytest tests/test_auth.py
python -m pytest tests/test_stock_data.py
python -m pytest tests/test_watchlist.py
```

### 测试覆盖

- 用户认证功能测试
- 股票数据管理测试
- 关注列表功能测试
- 权限控制测试
- API接口测试

## 📝 开发指南

### 代码结构

- **Models**: 数据模型定义
- **Repositories**: 数据访问层，封装数据库操作
- **Services**: 业务逻辑层，处理复杂业务逻辑
- **Views**: 视图控制层，处理HTTP请求
- **Templates**: 前端模板，使用Jinja2语法
- **Utils**: 工具函数，包含权限控制、验证等

### 开发规范

1. **代码风格**: 遵循PEP 8规范
2. **注释规范**: 使用中文注释，详细说明函数功能
3. **错误处理**: 统一的错误处理和响应格式
4. **日志记录**: 关键操作记录日志
5. **测试覆盖**: 新功能必须包含测试用例

### 添加新功能

1. 在 `models/` 中定义数据模型
2. 在 `repositories/` 中实现数据访问
3. 在 `services/` 中实现业务逻辑
4. 在 `views/` 中实现视图控制
5. 在 `templates/` 中创建前端模板
6. 添加相应的测试用例

## 🚀 部署指南

### 生产环境部署

1. **环境准备**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 配置环境变量
   cp env.example .env
   # 编辑 .env 文件，设置生产环境配置
   ```

2. **数据库迁移**
   ```bash
   # 初始化数据库
   python scripts/init_db.py
   
   # 导入股票数据
   python scripts/import_stocks.py
   
   # 创建管理员账户
   python scripts/setup_admin_user.py
   
   # 初始化AI配置
   python scripts/init_ai_configs.py
   ```

3. **启动服务**
   ```bash
   # 使用Gunicorn启动
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   
   # 或使用Docker
   docker-compose up -d
   ```

### Docker部署

```bash
# 构建镜像
docker build -t equitycompass .

# 运行容器
docker run -d -p 5000:5000 --env-file .env equitycompass

# 或使用Docker Compose
docker-compose up -d
```

## 🗄️ 数据库迁移指南

### 从SQLite迁移到MySQL

系统采用Repository模式和SQLAlchemy ORM，支持无缝数据库迁移。

#### 迁移优势

| 方面 | SQLite | MySQL |
|------|--------|-------|
| **并发性能** | 有限 | 优秀 |
| **数据完整性** | 基础 | 强大 |
| **备份恢复** | 文件复制 | 专业工具 |
| **扩展性** | 单机 | 集群支持 |
| **监控** | 基础 | 丰富 |

#### 迁移步骤

**1. 安装MySQL驱动**

```bash
# 安装MySQL Python驱动
pip install pymysql

# 或使用官方驱动
pip install mysqlclient
```

**2. 更新依赖文件**

编辑 `requirements.txt`：
```bash
# 取消注释并修改
pymysql==1.1.0  # 或 mysqlclient==2.2.0
```

**3. 配置数据库连接**

更新 `.env` 文件：
```bash
# MySQL配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/equitycompass

# 或使用官方驱动
# DATABASE_URL=mysql+mysqldb://username:password@localhost:3306/equitycompass
```

**4. 创建MySQL数据库**

```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE equitycompass CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'equitycompass'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON equitycompass.* TO 'equitycompass'@'localhost';
FLUSH PRIVILEGES;
```

**5. 执行数据库迁移**

```bash
# 生成迁移文件
flask db migrate -m "Switch to MySQL"

# 应用迁移
flask db upgrade

# 验证迁移
flask db current
```

**6. 数据迁移（可选）**

如果需要迁移现有SQLite数据：

```bash
# 导出SQLite数据
python scripts/export_sqlite_data.py

# 导入到MySQL
python scripts/import_mysql_data.py
```

**7. 验证迁移**

```bash
# 测试数据库连接
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    print('数据库连接成功:', db.engine.url)
    print('表数量:', len(db.metadata.tables))
"

# 运行应用测试
python scripts/run_all_tests.py
```

#### 生产环境配置

**MySQL优化配置**

```ini
# my.cnf 优化配置
[mysqld]
# 基础配置
default-storage-engine = InnoDB
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 性能优化
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# 连接配置
max_connections = 200
max_connect_errors = 1000
wait_timeout = 28800
interactive_timeout = 28800

# 查询缓存
query_cache_type = 1
query_cache_size = 64M
query_cache_limit = 2M
```

**环境变量配置**

```bash
# 生产环境 .env
FLASK_ENV=production
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/equitycompass

# 连接池配置
SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 20, "pool_recycle": 3600, "pool_pre_ping": True}
```

#### 迁移注意事项

1. **文件存储不变**：任务和报告文件存储方式保持不变
2. **备份策略**：迁移前务必备份SQLite数据库
3. **测试验证**：迁移后充分测试所有功能
4. **监控配置**：配置MySQL监控和日志
5. **性能调优**：根据实际负载调整MySQL参数

#### 回滚方案

如果迁移出现问题，可以快速回滚：

```bash
# 恢复SQLite配置
DATABASE_URL=sqlite:///equitycompass.db

# 恢复原始数据
cp backup/equitycompass.db .

# 重启应用
python run.py
```

### 从MySQL迁移到PostgreSQL

系统同样支持PostgreSQL：

```bash
# 安装PostgreSQL驱动
pip install psycopg2-binary

# 配置连接
DATABASE_URL=postgresql://username:password@localhost:5432/equitycompass

# 执行迁移
flask db migrate -m "Switch to PostgreSQL"
flask db upgrade
```

## 🔧 故障排除

### Docker部署常见问题

#### 1. 数据库只读错误
**错误信息**: `(sqlite3.OperationalError) attempt to write a readonly database`

**解决方案**:
```bash
# 方法1: 在容器内修复权限
docker exec -it equitycompass-app bash
chmod 664 /app/instance/*.db
chmod 755 /app/instance/

# 方法2: 重新创建数据卷
docker-compose down
docker volume rm equitycompass_data
docker-compose up -d
```

#### 2. 服务器内部错误
**错误信息**: `{"error":"INTERNAL_ERROR","message":"服务器内部错误","success":false}`

**调试步骤**:
```bash
# 查看详细日志
docker-compose logs --tail=100 equitycompass

# 检查容器状态
docker-compose ps

# 进入容器调试
docker exec -it equitycompass-app bash
cd /app
python -c "from app import create_app; app = create_app(); print('应用创建成功')"
```

#### 3. 数据库初始化失败
**解决方案**:
```bash
# 进入容器手动初始化
docker exec -it equitycompass-app bash
cd /app
python scripts/init_db.py
python scripts/import_stocks.py
python scripts/setup_admin_user.py
python scripts/init_ai_configs.py
```

#### 4. 端口占用问题
**解决方案**:
```bash
# 检查端口占用
netstat -tlnp | grep 5002

# 修改docker-compose.yml中的端口映射
# 将 "5002:5002" 改为 "5003:5002"
```

#### 5. 环境变量配置问题
**检查方法**:
```bash
# 检查环境变量
docker exec -it equitycompass-app env | grep -E "(FLASK|DATABASE|AI)"

# 检查.env文件
docker exec -it equitycompass-app cat /app/.env
```

### 本地开发常见问题

#### 1. 模块导入错误
**解决方案**:
```bash
# 确保在正确的目录
cd backend

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 数据库连接问题
**解决方案**:
```bash
# 重新初始化数据库
python scripts/clear_all_data.py --force
python scripts/init_db.py
python scripts/import_stocks.py
python scripts/setup_admin_user.py
```

#### 3. AI模型调用失败
**检查项目**:
- 确认API密钥配置正确
- 检查网络连接
- 验证模型名称和提供商配置

### 日志查看

#### Docker环境
```bash
# 实时查看日志
docker-compose logs -f equitycompass

# 查看最近100行日志
docker-compose logs --tail=100 equitycompass

# 查看特定时间段的日志
docker-compose logs --since="2025-09-07T10:00:00" equitycompass
```

#### 本地环境
```bash
# 查看应用日志
tail -f app.log

# 查看错误日志
tail -f error.log
```

### 性能优化

#### 1. 数据库优化
```bash
# 清理旧数据
python scripts/clear_all_data.py --status

# 重建数据库索引
python scripts/recreate_tables.py
```

#### 2. 内存优化
```bash
# 清理Docker缓存
docker system prune -a

# 限制容器内存使用
# 在docker-compose.yml中添加:
# deploy:
#   resources:
#     limits:
#       memory: 1G
```

## 📚 文档

- [系统架构文档](docs/architecture/)
- [API设计文档](docs/api/)
- [数据库设计文档](docs/database/)
- [部署指南](docs/deployment/)
- [开发日志](DEVELOPMENT_LOG.md)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 项目地址: https://github.com/your-username/EquityCompass
- 问题反馈: https://github.com/your-username/EquityCompass/issues
- 邮箱: admin@equitycompass.com

## 📋 更新日志

### v1.2.0 (2025-09-06)

#### 🚀 新功能
- **AI配置管理**: 新增动态AI模型配置管理功能
- **提示词管理**: 支持提示词版本管理和自定义编辑
- **任务重试机制**: 智能任务重试，失败任务自动重新调用AI模型
- **权限控制优化**: 完善的三级权限体系，细粒度权限控制

#### 🔧 功能改进
- **AI模型调用**: 优化AI模型调用逻辑，优先使用数据库配置
- **任务管理**: 改进任务状态跟踪和错误处理
- **用户界面**: 优化管理员界面，添加工具提示和状态指示
- **报告系统**: 改进报告生成和下载权限控制

#### 🐛 问题修复
- 修复AI模型配置优先级问题
- 修复任务重试机制中的线程问题
- 修复提示词管理中的模板渲染错误
- 修复批量任务创建中的参数传递问题
- 修复报告统计页面的权限控制问题

#### 📚 文档更新
- 更新API接口文档
- 添加数据库迁移指南
- 完善部署和配置说明
- 更新开发指南和测试说明

### v1.1.0 (2025-09-05)

#### 🚀 新功能
- **多用户系统**: 完整的用户注册、登录和权限管理
- **关注列表**: 个性化股票关注和监控功能
- **报告导出**: PDF格式报告导出功能
- **管理员功能**: 用户管理和数据统计功能

#### 🔧 功能改进
- 优化股票数据管理
- 改进分析任务执行效率
- 增强错误处理和日志记录

### v1.0.0 (2025-09-04)

#### 🎉 初始版本
- 基础股票分析功能
- AI模型集成（DeepSeek、OpenAI、Qwen、Gemini）
- 股票池管理
- 分析报告生成

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**智策股析** - 让AI为您的投资决策提供专业洞察 🚀