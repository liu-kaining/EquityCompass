# Gmail邮件服务配置指南

本文档详细说明如何配置Gmail作为智策股析的邮件服务提供商。

## 📧 为什么选择Gmail？

### ✅ 优势
- **免费**：每天可发送500封邮件
- **稳定**：Google的可靠基础设施
- **安全**：TLS加密，两步验证
- **易用**：配置简单，文档完善
- **国际化**：支持多语言邮件

### ⚠️ 限制
- **发送限制**：每天最多500封
- **需要两步验证**：必须开启才能使用SMTP
- **应用专用密码**：不能使用账户密码

## 🔐 第一步：开启Gmail两步验证

### 1. 登录Google账户
访问 [myaccount.google.com](https://myaccount.google.com)

### 2. 进入安全设置
- 点击左侧菜单的"安全性"
- 找到"登录Google"部分

### 3. 开启两步验证
1. 点击"两步验证"
2. 点击"开始使用"
3. 选择验证方式（推荐手机短信）
4. 输入验证码
5. 确认开启

**重要**：两步验证是使用Gmail SMTP的必要条件！

## 🔑 第二步：生成应用专用密码

### 1. 访问应用专用密码页面
- 在两步验证页面，找到"应用专用密码"
- 或者直接访问：[myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### 2. 生成新密码
1. 点击"生成新的应用专用密码"
2. 选择应用类型：**选择"其他（自定义名称）"**
3. 输入名称：`智策股析邮件服务`
4. 点击"生成"

### 3. 保存密码
- 系统会生成一个16位的应用专用密码
- **格式示例**：`abcd efgh ijkl mnop`
- **重要**：立即复制并保存这个密码，它只会显示一次！

## ⚙️ 第三步：配置环境变量

### 开发环境配置

在项目根目录创建 `.env` 文件：

```bash
# Gmail邮件服务配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=智策股析
SEND_EMAIL=true
```

### 生产环境配置

在生产服务器的 `.env` 文件中添加：

```bash
# Gmail邮件服务配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=智策股析
SEND_EMAIL=true

# 其他生产环境配置
FLASK_ENV=production
DEBUG=false
```

## 🧪 第四步：测试邮件服务

### 使用测试脚本

我创建了一个专门的测试脚本来验证Gmail配置：

```bash
# 设置环境变量
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-16-digit-app-password
export FROM_EMAIL=your-email@gmail.com
export FROM_NAME=智策股析

# 运行测试脚本
python scripts/test_email.py
```

### 手动测试

你也可以使用Python手动测试：

```python
import smtplib
from email.mime.text import MIMEText

# 配置
smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "your-email@gmail.com"
password = "your-16-digit-app-password"

# 创建邮件
msg = MIMEText("这是一封测试邮件")
msg['Subject'] = "Gmail SMTP测试"
msg['From'] = username
msg['To'] = "test@example.com"

# 发送邮件
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
```

## 🔧 第五步：集成到应用

### 1. 重启应用服务

配置完成后，重启Flask应用：

```bash
# 开发环境
cd backend
python app.py

# 生产环境
sudo systemctl restart equitycompass
```

### 2. 测试用户注册流程

1. 访问应用登录页面
2. 输入邮箱地址
3. 点击"发送验证码"
4. 检查邮箱是否收到验证码邮件

## 🚨 常见问题解决

### 问题1：认证失败 (535, b'Username and Password not accepted')

**原因**：应用专用密码错误或未开启两步验证

**解决方案**：
1. 确认已开启两步验证
2. 重新生成应用专用密码
3. 检查密码格式（16位，包含空格）

### 问题2：连接超时

**原因**：网络问题或防火墙阻止

**解决方案**：
1. 检查网络连接
2. 确认防火墙允许587端口
3. 尝试使用465端口（SSL）

### 问题3：邮件发送失败

**原因**：Gmail发送限制或配置错误

**解决方案**：
1. 检查每日发送限制（500封/天）
2. 确认FROM_EMAIL与SMTP_USERNAME一致
3. 检查邮件内容格式

## 📊 Gmail SMTP配置参考

| 配置项 | 值 | 说明 |
|--------|----|----|
| **SMTP服务器** | smtp.gmail.com | Gmail SMTP服务器地址 |
| **端口** | 587 | TLS端口（推荐） |
| **加密** | TLS | 传输层安全加密 |
| **认证** | 必需 | 用户名+应用专用密码 |
| **发送限制** | 500封/天 | 免费账户限制 |

## 🔒 安全建议

### 1. 密码安全
- 使用应用专用密码，不要使用账户密码
- 定期更换应用专用密码
- 不要在代码中硬编码密码

### 2. 环境变量
- 使用环境变量存储敏感信息
- 不要将 `.env` 文件提交到版本控制
- 在生产环境使用强密钥

### 3. 监控和日志
- 监控邮件发送成功率
- 记录邮件发送日志
- 设置发送失败告警

## 📈 性能优化

### 1. 连接池
```python
# 使用连接池提高性能
from smtplib import SMTP_SSL
import threading

class EmailConnectionPool:
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
```

### 2. 异步发送
```python
# 使用Celery异步发送邮件
from celery import Celery

@celery.task
def send_email_async(to_email, subject, content):
    # 异步发送邮件逻辑
    pass
```

### 3. 批量发送
```python
# 批量发送邮件
def send_bulk_emails(emails, template):
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        for email in emails:
            # 发送邮件
            pass
```

## 🎯 最佳实践

### 1. 邮件模板
- 使用HTML和纯文本双重格式
- 包含品牌标识和联系方式
- 提供退订链接

### 2. 发送频率
- 控制发送频率，避免被标记为垃圾邮件
- 实现发送队列和重试机制
- 监控发送成功率

### 3. 错误处理
- 实现优雅的错误处理
- 记录详细的错误日志
- 提供备用邮件服务

## 📞 技术支持

如果遇到问题，可以：

1. **查看Gmail帮助文档**：[Gmail SMTP设置](https://support.google.com/mail/answer/7126229)
2. **检查应用日志**：查看详细的错误信息
3. **使用测试脚本**：运行 `scripts/test_email.py` 进行诊断
4. **联系开发团队**：提交Issue或Pull Request

---

*最后更新: 2025-08-20*
*维护者: 智策股析开发团队*
