# 支付宝支付配置指南

## 1. 注册支付宝开放平台

1. 访问 [支付宝开放平台](https://open.alipay.com/)
2. 注册开发者账号
3. 完成实名认证

## 2. 创建应用

1. 登录开放平台控制台
2. 点击"创建应用"
3. 选择"网页&移动应用"
4. 填写应用信息：
   - 应用名称：智策股析
   - 应用描述：股票分析系统
   - 应用图标：上传应用图标

## 3. 配置应用

### 3.1 添加功能
- 网页支付
- 手机网站支付
- 电脑网站支付

### 3.2 设置回调地址
- 授权回调地址：`https://yourdomain.com/auth/alipay/callback`
- 支付回调地址：`https://yourdomain.com/api/payment/alipay/notify`

### 3.3 获取密钥
1. 生成应用私钥
2. 上传公钥到支付宝
3. 获取支付宝公钥

## 4. 环境变量配置

```bash
ALIPAY_APP_ID=你的应用ID
ALIPAY_PRIVATE_KEY=你的应用私钥
ALIPAY_PUBLIC_KEY=支付宝公钥
ALIPAY_NOTIFY_URL=https://yourdomain.com/api/payment/alipay/notify
ALIPAY_RETURN_URL=https://yourdomain.com/payment/success
```

## 5. 测试

1. 使用沙箱环境测试
2. 验证支付回调
3. 测试退款功能

## 6. 上线

1. 提交审核
2. 审核通过后正式上线
3. 监控支付状态
