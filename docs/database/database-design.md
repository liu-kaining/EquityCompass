# 智策股析 - 数据库设计

## 概述

智策股析采用混合存储方案：
- **结构化数据**: PostgreSQL/SQLite存储用户、订阅、任务状态等
- **分析报告**: JSON文件存储，便于导出和版本管理
- **缓存层**: Redis存储验证码、会话、临时数据

## 数据库表结构

### 1. 用户相关表

#### users (用户表)
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL COMMENT '邮箱地址，唯一标识',
    nickname VARCHAR(100) COMMENT '用户昵称',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE COMMENT '账户是否激活'
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### user_plans (用户计划表)
```sql
CREATE TABLE user_plans (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type VARCHAR(50) NOT NULL COMMENT 'TRIAL/FREE/SUBSCRIPTION/PAY_PER_USE',
    plan_start_date TIMESTAMP,
    plan_end_date TIMESTAMP,
    remaining_quota INTEGER DEFAULT 0 COMMENT '剩余分析次数',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_user_plans_user_id ON user_plans(user_id);
CREATE INDEX idx_user_plans_plan_type ON user_plans(plan_type);
CREATE INDEX idx_user_plans_active ON user_plans(is_active);
```

### 2. 股票相关表

#### stocks (股票表)
```sql
CREATE TABLE stocks (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL COMMENT '股票代码，如AAPL或00700.HK',
    name VARCHAR(200) NOT NULL COMMENT '公司名称',
    market VARCHAR(10) NOT NULL COMMENT 'US/HK',
    exchange VARCHAR(50) COMMENT 'NASDAQ/HKEX等',
    industry VARCHAR(100) COMMENT '行业分类',
    stock_type VARCHAR(20) DEFAULT 'BUILT_IN' COMMENT 'BUILT_IN/USER_CUSTOM',
    created_by_user_id BIGINT REFERENCES users(id) COMMENT '自定义股票的创建者',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_stocks_code ON stocks(code);
CREATE INDEX idx_stocks_market ON stocks(market);
CREATE INDEX idx_stocks_industry ON stocks(industry);
CREATE INDEX idx_stocks_type ON stocks(stock_type);
CREATE INDEX idx_stocks_creator ON stocks(created_by_user_id);
```

#### user_watchlists (用户关注列表)
```sql
CREATE TABLE user_watchlists (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_id BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, stock_id)
);

-- 索引
CREATE INDEX idx_watchlists_user_id ON user_watchlists(user_id);
CREATE INDEX idx_watchlists_stock_id ON user_watchlists(stock_id);
```

### 3. 分析任务相关表

#### analysis_tasks (分析任务表)
```sql
CREATE TABLE analysis_tasks (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    stock_id BIGINT NOT NULL REFERENCES stocks(id),
    task_id VARCHAR(255) UNIQUE NOT NULL COMMENT 'Celery任务ID',
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING/PROCESSING/SUCCESS/FAILED',
    analysis_date DATE NOT NULL COMMENT '分析日期 YYYY-MM-DD',
    prompt_version VARCHAR(50) COMMENT '使用的Prompt版本',
    llm_model VARCHAR(100) COMMENT '使用的LLM模型',
    error_message TEXT COMMENT '失败时的错误信息',
    retry_count INTEGER DEFAULT 0 COMMENT '重试次数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP COMMENT '完成时间'
);

-- 索引
CREATE INDEX idx_analysis_tasks_user_id ON analysis_tasks(user_id);
CREATE INDEX idx_analysis_tasks_stock_id ON analysis_tasks(stock_id);
CREATE INDEX idx_analysis_tasks_status ON analysis_tasks(status);
CREATE INDEX idx_analysis_tasks_date ON analysis_tasks(analysis_date);
CREATE INDEX idx_analysis_tasks_task_id ON analysis_tasks(task_id);
```

#### prompt_templates (Prompt模板表)
```sql
CREATE TABLE prompt_templates (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL COMMENT '模板名称',
    version VARCHAR(50) NOT NULL COMMENT '版本号',
    content TEXT NOT NULL COMMENT 'Prompt内容',
    is_active BOOLEAN DEFAULT FALSE COMMENT '是否为当前使用版本',
    template_type VARCHAR(50) COMMENT 'TECHNICAL/FUNDAMENTAL/COMPREHENSIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE(name, version)
);

-- 索引
CREATE INDEX idx_prompt_templates_active ON prompt_templates(is_active);
CREATE INDEX idx_prompt_templates_type ON prompt_templates(template_type);
```

### 4. 报告索引表

#### report_index (报告索引表)
```sql
CREATE TABLE report_index (
    id BIGSERIAL PRIMARY KEY,
    stock_id BIGINT NOT NULL REFERENCES stocks(id),
    analysis_date DATE NOT NULL COMMENT '分析日期 YYYY-MM-DD',
    file_path VARCHAR(500) NOT NULL COMMENT 'JSON文件路径',
    summary TEXT COMMENT '报告摘要',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by_task_id BIGINT REFERENCES analysis_tasks(id),
    UNIQUE(stock_id, analysis_date)
);

-- 索引
CREATE INDEX idx_report_index_stock_date ON report_index(stock_id, analysis_date);
CREATE INDEX idx_report_index_date ON report_index(analysis_date);
CREATE INDEX idx_report_index_generated_at ON report_index(generated_at);
```

### 5. 邮件订阅表

#### email_subscriptions (邮件订阅表)
```sql
CREATE TABLE email_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_subscribed BOOLEAN DEFAULT TRUE COMMENT '是否订阅每日邮件',
    frequency VARCHAR(20) DEFAULT 'DAILY' COMMENT '发送频率',
    last_sent_at TIMESTAMP COMMENT '最后发送时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_email_subscriptions_user_id ON email_subscriptions(user_id);
CREATE INDEX idx_email_subscriptions_subscribed ON email_subscriptions(is_subscribed);
```

### 6. 支付相关表

#### payment_transactions (支付交易表)
```sql
CREATE TABLE payment_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    transaction_id VARCHAR(255) UNIQUE NOT NULL COMMENT '第三方支付ID',
    payment_provider VARCHAR(50) NOT NULL COMMENT 'STRIPE/PADDLE',
    amount DECIMAL(10,2) NOT NULL COMMENT '金额',
    currency VARCHAR(3) DEFAULT 'USD' COMMENT '货币类型',
    transaction_type VARCHAR(50) NOT NULL COMMENT 'SUBSCRIPTION/ONE_TIME',
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING/SUCCESS/FAILED/REFUNDED',
    raw_response JSON COMMENT '支付网关原始响应',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_payment_transactions_user_id ON payment_transactions(user_id);
CREATE INDEX idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX idx_payment_transactions_provider ON payment_transactions(payment_provider);
CREATE INDEX idx_payment_transactions_transaction_id ON payment_transactions(transaction_id);
```

### 7. 管理员相关表

#### admins (管理员表)
```sql
CREATE TABLE admins (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'ADMIN' COMMENT 'SUPER_ADMIN/ADMIN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 索引
CREATE INDEX idx_admins_username ON admins(username);
CREATE INDEX idx_admins_role ON admins(role);
```

#### system_configs (系统配置表)
```sql
CREATE TABLE system_configs (
    id BIGSERIAL PRIMARY KEY,
    config_key VARCHAR(200) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_system_configs_key ON system_configs(config_key);
```

## 文件存储结构

### 报告文件组织
```
/data/
├── reports/                    # 分析报告存储
│   ├── 2025-01-20/            # 按日期分组
│   │   ├── AAPL.json          # 股票代码为文件名
│   │   ├── 00700.HK.json
│   │   └── TSLA.json
│   ├── 2025-01-21/
│   │   └── ...
│   └── 2025-01-22/
│       └── ...
├── exports/                    # 导出文件
│   ├── temp/                  # 临时导出文件
│   │   ├── user_123_20250120.zip
│   │   └── ...
│   └── user_exports/          # 用户导出历史
│       ├── 2025-01/
│       └── ...
├── backups/                   # 备份文件
│   ├── daily/
│   └── weekly/
└── logs/                      # 日志文件
    ├── celery/
    ├── analysis/
    └── system/
```

### JSON报告文件格式
```json
{
    "stockCode": "AAPL",
    "companyName": "Apple Inc.",
    "market": "US",
    "exchange": "NASDAQ",
    "industry": "Technology",
    "analysisDate": "2025-01-20",
    "promptVersion": "v1.2",
    "llmModel": "gemini-pro",
    "generatedAt": "2025-01-20T04:15:30Z",
    "reportContent": "# Apple Inc. (AAPL) 每日分析报告\n\n## 技术分析\n...",
    "reportSummary": "苹果股价今日小幅上涨，技术指标显示...",
    "metadata": {
        "taskId": "celery-task-uuid",
        "analysisTimeMs": 2450,
        "retryCount": 0
    }
}
```

## Redis缓存结构

### 缓存键命名规范
```
# 验证码缓存 (TTL: 10分钟)
auth:verification_code:{email} = "123456"

# 用户会话缓存 (TTL: 30天)
session:user:{user_id} = {user_info_json}

# 报告缓存 (TTL: 24小时)
report:cache:{stock_code}:{date} = {report_json}

# 任务状态缓存 (TTL: 1小时)
task:status:{task_id} = {status_info}

# 接口限流 (TTL: 1分钟)
rate_limit:auth:{email} = {attempt_count}
```

## 数据库优化策略

### 1. 索引优化
- 为高频查询字段创建索引
- 复合索引优化多条件查询
- 定期分析和优化慢查询

### 2. 分区策略
- `analysis_tasks`表按月分区
- `report_index`表按月分区
- 自动清理历史数据

### 3. 读写分离
- 主库处理写操作
- 从库处理读操作和分析查询
- 报告生成优先使用从库

### 4. 缓存策略
- 热门股票报告缓存
- 用户关注列表缓存
- 系统配置缓存

## 数据备份策略

### 1. 数据库备份
- 每日增量备份
- 每周全量备份
- 异地备份存储

### 2. 文件备份
- 报告文件每日备份
- 重要文件多副本存储
- 定期备份验证

### 3. 恢复策略
- RTO目标: 4小时内
- RPO目标: 1小时内
- 定期恢复演练

---

*此文档详细定义了智策股析项目的数据存储架构，为开发和运维提供数据层面的技术指导。*
