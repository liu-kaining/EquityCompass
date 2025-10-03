# 💳 金币购买支付系统使用指南

## 🎯 系统概述

本系统支持多种支付方式购买金币，包括：
- **支付宝** - 适合国内用户
- **微信支付** - 适合国内用户  
- **Stripe** - 适合国际用户

## 🚀 快速开始

### 1. 开发环境测试

在开发环境中，系统使用模拟支付，无需真实支付配置：

```bash
# 启动应用
python run.py

# 访问金币中心
http://localhost:5002/coin

# 选择套餐，点击购买
# 系统会显示模拟支付对话框
# 可以选择"支付成功"或"支付失败"进行测试
```

### 2. 生产环境配置

#### 2.1 支付宝配置

1. 注册支付宝开放平台账号
2. 创建应用并获取：
   - `APP_ID`
   - `应用私钥`
   - `支付宝公钥`

3. 配置环境变量：
```bash
ALIPAY_APP_ID=your_app_id
ALIPAY_PRIVATE_KEY=your_private_key
ALIPAY_PUBLIC_KEY=your_public_key
ALIPAY_NOTIFY_URL=https://yourdomain.com/api/payment/alipay/notify
ALIPAY_RETURN_URL=https://yourdomain.com/payment/success
```

#### 2.2 微信支付配置

1. 注册微信商户平台账号
2. 获取：
   - `APP_ID`
   - `商户号(MCH_ID)`
   - `API密钥`

3. 配置环境变量：
```bash
WECHAT_APP_ID=your_app_id
WECHAT_MCH_ID=your_mch_id
WECHAT_API_KEY=your_api_key
WECHAT_NOTIFY_URL=https://yourdomain.com/api/payment/wechat/notify
```

#### 2.3 Stripe配置

1. 注册Stripe账号
2. 获取：
   - `Publishable Key`
   - `Secret Key`
   - `Webhook Secret`

3. 配置环境变量：
```bash
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

## 📱 支付流程

### 用户支付流程

1. **选择套餐** - 用户在金币中心选择要购买的金币套餐
2. **选择支付方式** - 选择支付宝、微信支付或Stripe
3. **创建订单** - 系统创建金币订单和支付订单
4. **完成支付** - 根据支付方式：
   - **支付宝**: 跳转到支付宝支付页面
   - **微信支付**: 显示二维码供用户扫描
   - **Stripe**: 显示Stripe支付表单
5. **支付验证** - 系统验证支付结果
6. **金币到账** - 支付成功后金币自动到账

### 支付状态轮询

系统会自动轮询支付状态：
- 每5秒检查一次支付状态
- 最多轮询30次（2.5分钟）
- 支付成功后自动刷新用户金币余额

## 🔧 API接口

### 创建支付订单

```http
POST /api/coin/order
Content-Type: application/json

{
    "package_id": 1,
    "payment_method": "ALIPAY"
}
```

**响应示例：**
```json
{
    "success": true,
    "data": {
        "order_id": 123,
        "order_no": "COIN_20251003_12345678",
        "payment_url": "https://openapi.alipay.com/gateway.do?...",
        "amount": 9.9,
        "coins": 100,
        "payment_method": "ALIPAY"
    }
}
```

### 查询订单状态

```http
GET /api/coin/order/status/{order_no}
```

**响应示例：**
```json
{
    "success": true,
    "data": {
        "order_no": "COIN_20251003_12345678",
        "status": "PAID",
        "amount": 9.9,
        "coins": 100,
        "created_at": "2025-10-03T19:30:00",
        "paid_at": "2025-10-03T19:31:00"
    }
}
```

### 支付回调接口

#### 支付宝回调
```http
POST /api/payment/webhook/alipay
Content-Type: application/x-www-form-urlencoded
```

#### 微信支付回调
```http
POST /api/payment/webhook/wechat
Content-Type: application/xml
```

#### Stripe回调
```http
POST /api/payment/webhook/stripe
Content-Type: application/json
```

## 🛠️ 开发测试

### 模拟支付测试

在开发环境中，系统提供模拟支付功能：

```javascript
// 模拟支付成功
POST /api/payment/mock/success/{mock_payment_id}

// 模拟支付失败
POST /api/payment/mock/failure/{mock_payment_id}
```

### 测试用例

1. **正常支付流程测试**
   - 创建订单
   - 模拟支付成功
   - 验证金币到账

2. **支付失败测试**
   - 创建订单
   - 模拟支付失败
   - 验证订单状态

3. **支付超时测试**
   - 创建订单
   - 不进行支付
   - 验证超时处理

## 🔒 安全考虑

### 1. 支付安全
- 所有支付请求都经过签名验证
- 支付回调URL使用HTTPS
- 敏感信息加密存储

### 2. 订单安全
- 订单号使用时间戳+随机数生成
- 订单状态变更记录完整日志
- 防止重复支付

### 3. 数据安全
- 支付信息不在前端存储
- 数据库连接使用SSL
- 定期备份支付数据

## 📊 监控和日志

### 支付监控
- 支付成功率统计
- 支付失败原因分析
- 订单处理时间监控

### 日志记录
- 所有支付操作记录详细日志
- 支付回调请求记录
- 异常情况告警

## 🚨 故障处理

### 常见问题

1. **支付回调失败**
   - 检查回调URL配置
   - 验证签名算法
   - 查看服务器日志

2. **订单状态不一致**
   - 手动查询支付状态
   - 重新处理订单
   - 联系支付平台客服

3. **金币未到账**
   - 检查订单状态
   - 验证支付记录
   - 手动补发金币

### 应急处理

1. **支付系统故障**
   - 切换到备用支付方式
   - 暂停新订单创建
   - 通知用户维护信息

2. **数据不一致**
   - 停止支付服务
   - 数据修复
   - 重新启动服务

## 📈 性能优化

### 1. 数据库优化
- 订单表添加索引
- 定期清理过期订单
- 使用读写分离

### 2. 缓存策略
- 支付方式配置缓存
- 订单状态缓存
- 用户金币余额缓存

### 3. 并发处理
- 使用数据库锁防止重复支付
- 异步处理支付回调
- 队列处理大量订单

## 🔄 版本更新

### 更新步骤
1. 备份当前配置
2. 更新代码
3. 测试支付功能
4. 逐步切换流量
5. 监控系统状态

### 回滚方案
1. 停止新支付请求
2. 恢复旧版本代码
3. 恢复配置
4. 重启服务

## 📞 技术支持

如有问题，请联系：
- 技术文档：查看项目README
- 问题反馈：提交GitHub Issue
- 紧急联系：联系开发团队

---

**注意：** 在生产环境使用前，请确保所有支付配置正确，并进行充分的测试。
