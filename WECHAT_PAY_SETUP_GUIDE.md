# 微信支付配置指南

## 1. 注册微信商户平台

1. 访问 [微信商户平台](https://pay.weixin.qq.com/)
2. 注册商户账号
3. 完成资质认证

## 2. 创建应用

1. 登录商户平台
2. 进入"产品中心"
3. 开通"Native支付"或"JSAPI支付"

## 3. 配置参数

### 3.1 获取必要参数
- APPID：微信公众号或小程序的APPID
- 商户号：MCH_ID
- API密钥：在商户平台设置

### 3.2 设置回调地址
- 支付回调：`https://yourdomain.com/api/payment/wechat/notify`

## 4. 环境变量配置

```bash
WECHAT_APP_ID=你的APPID
WECHAT_MCH_ID=你的商户号
WECHAT_API_KEY=你的API密钥
WECHAT_NOTIFY_URL=https://yourdomain.com/api/payment/wechat/notify
```

## 5. 测试

1. 使用沙箱环境测试
2. 验证支付回调
3. 测试退款功能

## 6. 上线

1. 提交审核
2. 审核通过后正式上线
3. 监控支付状态
