# Stripe支付配置指南

## 1. 注册Stripe账号

1. 访问 [Stripe官网](https://stripe.com/)
2. 注册账号
3. 完成账号验证

## 2. 获取API密钥

1. 登录Stripe Dashboard
2. 进入"Developers" > "API keys"
3. 获取以下密钥：
   - Publishable key (pk_live_...)
   - Secret key (sk_live_...)

## 3. 配置Webhook

1. 进入"Developers" > "Webhooks"
2. 添加端点：`https://yourdomain.com/api/payment/webhook/stripe`
3. 选择事件：`payment_intent.succeeded`
4. 获取Webhook签名密钥

## 4. 环境变量配置

```bash
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

## 5. 测试

1. 使用测试模式测试
2. 验证Webhook回调
3. 测试退款功能

## 6. 上线

1. 切换到Live模式
2. 更新API密钥
3. 监控支付状态
