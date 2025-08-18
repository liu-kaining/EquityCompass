# 智策股析 - API接口设计

## API设计原则

### 1. RESTful设计
- 使用标准HTTP方法：GET, POST, PUT, DELETE
- 资源导向的URL设计
- 无状态设计，通过JWT Token认证

### 2. 统一响应格式
```json
// 成功响应
{
    "success": true,
    "data": {},
    "message": "Success",
    "timestamp": "2025-01-20T12:00:00Z"
}

// 错误响应
{
    "success": false,
    "error": "ERROR_CODE",
    "message": "错误描述",
    "timestamp": "2025-01-20T12:00:00Z"
}
```

### 3. 状态码规范
- **200**: 请求成功
- **201**: 创建成功
- **400**: 请求参数错误
- **401**: 未认证
- **403**: 权限不足
- **404**: 资源不存在
- **429**: 请求过于频繁
- **500**: 服务器内部错误

## API接口详细设计

### 1. 认证相关API

#### 1.1 发送验证码
```http
POST /api/auth/send-code
Content-Type: application/json

{
    "email": "user@example.com"
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "message": "验证码已发送",
        "expires_in": 600
    }
}
```

**错误码**:
- `EMAIL_INVALID`: 邮箱格式无效
- `SEND_TOO_FREQUENT`: 发送过于频繁
- `EMAIL_SEND_FAILED`: 邮件发送失败

#### 1.2 验证登录
```http
POST /api/auth/verify-code
Content-Type: application/json

{
    "email": "user@example.com",
    "code": "123456"
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "token": "jwt_token_string",
        "user": {
            "id": 123,
            "email": "user@example.com",
            "nickname": "用户昵称",
            "created_at": "2025-01-20T12:00:00Z"
        }
    }
}
```

**错误码**:
- `CODE_INVALID`: 验证码错误
- `CODE_EXPIRED`: 验证码已过期
- `USER_DISABLED`: 用户被禁用

#### 1.3 登出
```http
POST /api/auth/logout
Authorization: Bearer {jwt_token}
```

#### 1.4 检查登录状态
```http
GET /api/auth/status
Authorization: Bearer {jwt_token}
```

### 2. 用户相关API

#### 2.1 获取用户信息
```http
GET /api/users/profile
Authorization: Bearer {jwt_token}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "id": 123,
        "email": "user@example.com",
        "nickname": "用户昵称",
        "created_at": "2025-01-20T12:00:00Z",
        "plan": {
            "type": "TRIAL",
            "remaining_quota": 1,
            "expires_at": "2025-01-27T12:00:00Z"
        }
    }
}
```

#### 2.2 更新用户信息
```http
PUT /api/users/profile
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
    "nickname": "新昵称"
}
```

#### 2.3 获取用户计划
```http
GET /api/users/plan
Authorization: Bearer {jwt_token}
```

### 3. 股票池API

#### 3.1 获取股票列表
```http
GET /api/stocks?market=US&page=1&limit=20&search=Apple
Authorization: Bearer {jwt_token}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "stocks": [
            {
                "id": 1,
                "code": "AAPL",
                "name": "苹果公司",
                "market": "US",
                "exchange": "NASDAQ",
                "industry": "Technology",
                "stock_type": "BUILT_IN"
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 100,
            "pages": 5
        }
    }
}
```

#### 3.2 搜索股票
```http
GET /api/stocks/search?q=Apple&market=US
Authorization: Bearer {jwt_token}
```

#### 3.3 添加自定义股票
```http
POST /api/stocks
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
    "code": "TSLA",
    "name": "特斯拉",
    "market": "US",
    "exchange": "NASDAQ",
    "industry": "Automotive"
}
```

#### 3.4 获取内置股票池
```http
GET /api/stocks/builtin?market=US
Authorization: Bearer {jwt_token}
```

### 4. 关注列表API

#### 4.1 获取关注列表
```http
GET /api/watchlist
Authorization: Bearer {jwt_token}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "stocks": [
            {
                "id": 1,
                "code": "AAPL",
                "name": "苹果公司",
                "market": "US",
                "added_at": "2025-01-20T12:00:00Z"
            }
        ],
        "count": 1,
        "max_count": 20
    }
}
```

#### 4.2 添加股票到关注列表
```http
POST /api/watchlist
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
    "stock_id": 123
}
```

**错误码**:
- `WATCHLIST_FULL`: 关注列表已满（最多20支）
- `STOCK_ALREADY_WATCHED`: 股票已在关注列表中

#### 4.3 移除关注股票
```http
DELETE /api/watchlist/{stock_id}
Authorization: Bearer {jwt_token}
```

### 5. 分析任务API

#### 5.1 触发分析任务
```http
POST /api/analysis/trigger
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
    "stock_ids": [1, 2, 3],  // 可选，不指定则分析全部关注列表
    "prompt_version": "v1.2",  // 可选，使用指定Prompt版本
    "llm_model": "gemini-pro"  // 可选，使用指定LLM模型
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "tasks": [
            {
                "task_id": "celery-uuid-123",
                "stock_id": 1,
                "stock_code": "AAPL",
                "status": "PENDING",
                "estimated_time": 120
            }
        ],
        "message": "分析任务已提交，预计2分钟完成"
    }
}
```

**错误码**:
- `QUOTA_EXCEEDED`: 分析额度不足
- `PLAN_EXPIRED`: 用户计划已过期
- `NO_STOCKS_TO_ANALYZE`: 没有可分析的股票

#### 5.2 获取任务状态
```http
GET /api/analysis/status?task_ids=uuid1,uuid2
Authorization: Bearer {jwt_token}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "tasks": [
            {
                "task_id": "uuid1",
                "status": "SUCCESS",
                "progress": 100,
                "result": {
                    "report_id": 456,
                    "file_path": "/data/reports/2025-01-20/AAPL.json"
                }
            },
            {
                "task_id": "uuid2",
                "status": "PROCESSING",
                "progress": 60,
                "estimated_remaining": 45
            }
        ]
    }
}
```

#### 5.3 获取分析历史
```http
GET /api/analysis/history?page=1&limit=20&status=SUCCESS
Authorization: Bearer {jwt_token}
```

### 6. 报告相关API

#### 6.1 获取报告列表
```http
GET /api/reports?date=2025-01-20&stock_code=AAPL&page=1&limit=20
Authorization: Bearer {jwt_token}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "reports": [
            {
                "id": 456,
                "stock_code": "AAPL",
                "company_name": "苹果公司",
                "analysis_date": "2025-01-20",
                "summary": "苹果股价今日小幅上涨...",
                "generated_at": "2025-01-20T04:15:30Z",
                "llm_model": "gemini-pro"
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 100
        }
    }
}
```

#### 6.2 获取报告详情
```http
GET /api/reports/{report_id}
Authorization: Bearer {jwt_token}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "id": 456,
        "stock_code": "AAPL",
        "company_name": "苹果公司",
        "market": "US",
        "analysis_date": "2025-01-20",
        "content": "# Apple Inc. (AAPL) 每日分析报告\n\n## 技术分析\n...",
        "summary": "苹果股价今日小幅上涨...",
        "metadata": {
            "prompt_version": "v1.2",
            "llm_model": "gemini-pro",
            "analysis_time_ms": 2450
        }
    }
}
```

#### 6.3 搜索报告
```http
GET /api/reports/search?q=技术分析&date_from=2025-01-01&date_to=2025-01-20
Authorization: Bearer {jwt_token}
```

#### 6.4 导出报告
```http
POST /api/reports/export
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
    "report_ids": [456, 789],
    "format": "PDF",  // MD, PDF, ZIP
    "email_result": false  // 是否邮件发送结果
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "export_id": "export-uuid-123",
        "status": "PROCESSING",
        "estimated_time": 30,
        "download_url": null  // 完成后提供下载链接
    }
}
```

### 7. 订阅付费API

#### 7.1 获取付费计划
```http
GET /api/payment/plans
```

**响应**:
```json
{
    "success": true,
    "data": {
        "plans": [
            {
                "id": "trial",
                "name": "试用计划",
                "price": 0,
                "currency": "USD",
                "quota": 1,
                "features": ["1次完整分析", "报告查看", "基础导出"]
            },
            {
                "id": "monthly",
                "name": "月度订阅",
                "price": 29.99,
                "currency": "USD", 
                "quota": -1,  // -1表示无限制
                "features": ["无限分析", "报告查看", "高级导出", "邮件订阅"]
            }
        ]
    }
}
```

#### 7.2 创建支付会话
```http
POST /api/payment/create-session
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
    "plan_id": "monthly",
    "success_url": "https://app.example.com/payment/success",
    "cancel_url": "https://app.example.com/payment/cancel"
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "session_id": "stripe-session-123",
        "payment_url": "https://checkout.stripe.com/pay/cs_xxx",
        "expires_at": "2025-01-20T13:00:00Z"
    }
}
```

#### 7.3 支付回调处理
```http
POST /api/payment/webhook
Content-Type: application/json
Stripe-Signature: signature_header

{
    // Stripe/Paddle webhook payload
}
```

#### 7.4 获取支付历史
```http
GET /api/payment/history?page=1&limit=20
Authorization: Bearer {jwt_token}
```

### 8. 邮件订阅API

#### 8.1 获取邮件设置
```http
GET /api/email/settings
Authorization: Bearer {jwt_token}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "is_subscribed": true,
        "frequency": "DAILY",
        "last_sent_at": "2025-01-20T05:00:00Z"
    }
}
```

#### 8.2 更新邮件设置
```http
PUT /api/email/settings
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
    "is_subscribed": false
}
```

#### 8.3 取消订阅（无需登录）
```http
POST /api/email/unsubscribe
Content-Type: application/json

{
    "email": "user@example.com",
    "token": "unsubscribe_token"  // 从邮件链接获取
}
```

### 9. 管理员API

#### 9.1 管理员登录
```http
POST /api/admin/login
Content-Type: application/json

{
    "username": "admin",
    "password": "password"
}
```

#### 9.2 用户管理
```http
GET /api/admin/users?page=1&limit=20&search=email
Authorization: Bearer {admin_token}
```

```http
PUT /api/admin/users/{user_id}/status
Authorization: Bearer {admin_token}
Content-Type: application/json

{
    "is_active": false
}
```

#### 9.3 股票池管理
```http
GET /api/admin/stocks?market=US&page=1&limit=50
Authorization: Bearer {admin_token}
```

```http
POST /api/admin/stocks
Authorization: Bearer {admin_token}
Content-Type: application/json

{
    "code": "GOOGL",
    "name": "谷歌",
    "market": "US",
    "exchange": "NASDAQ",
    "industry": "Technology"
}
```

#### 9.4 Prompt管理
```http
GET /api/admin/prompts
Authorization: Bearer {admin_token}
```

```http
POST /api/admin/prompts
Authorization: Bearer {admin_token}
Content-Type: application/json

{
    "name": "技术分析模板",
    "version": "v2.0",
    "content": "请分析以下股票的技术面...",
    "template_type": "TECHNICAL",
    "is_active": true
}
```

#### 9.5 任务监控
```http
GET /api/admin/tasks?status=FAILED&page=1&limit=20
Authorization: Bearer {admin_token}
```

### 10. 系统监控API

#### 10.1 健康检查
```http
GET /api/health
```

**响应**:
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "timestamp": "2025-01-20T12:00:00Z",
        "services": {
            "database": "healthy",
            "redis": "healthy",
            "celery": "healthy"
        }
    }
}
```

#### 10.2 系统指标
```http
GET /api/health/metrics
Authorization: Bearer {admin_token}
```

## API中间件

### 1. 认证中间件
- JWT Token验证
- 用户权限检查
- 会话管理

### 2. 频率限制
- 基于IP和用户的请求限制
- 动态调整限制规则
- 优雅降级处理

### 3. 错误处理
- 统一异常捕获
- 详细错误日志
- 用户友好的错误信息

### 4. 请求日志
- 完整请求响应日志
- 性能监控数据
- 用户行为追踪

### 5. 跨域支持
- CORS配置
- 预检请求处理
- 安全头设置

## API版本管理

### 版本策略
- URL路径版本控制：`/api/v1/users`
- 向后兼容原则
- 逐步废弃旧版本

### 版本发布流程
1. 新版本并行开发
2. 灰度测试验证
3. 正式发布切换
4. 旧版本废弃通知

---

*此文档详细定义了智策股析项目的API接口规范，为前后端开发提供统一的接口标准。*
