# 邀请码系统API测试指南

## 前置条件

### 1. 数据库迁移
首先需要创建数据库表。有两种方式：

#### 方式1：使用Flask-Migrate（推荐）
```bash
cd backend
source venv/bin/activate
flask db migrate -m "Add invitation code system"
flask db upgrade
```

#### 方式2：直接创建表（开发环境）
```bash
cd backend
source venv/bin/activate
python -c "
from app import create_app, db
from app.models import InvitationCode

app = create_app('development')
with app.app_context():
    db.create_all()
    print('✅ 数据库表创建成功')
"
```

### 2. 启动应用
```bash
cd backend
source venv/bin/activate
python run.py
```

应用会在 `http://localhost:5002` 启动。

### 3. 确认管理员账户存在
```bash
cd backend
source venv/bin/activate
python -c "
from app import create_app, db
from app.models.user import User

app = create_app('development')
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f'✅ 管理员存在: {admin.username}, 角色: {admin.user_role}')
    else:
        print('❌ 管理员不存在，请先创建')
"
```

---

## API端点列表

### 管理员API（需要超级管理员权限）

#### 1. 生成邀请码
```http
POST /api/admin/invitation-codes/generate
Content-Type: application/json

{
    "count": 1  // 1-10之间
}
```

**响应**：
```json
{
    "success": true,
    "data": {
        "id": 1,
        "code": "ABCD1234567890EFGH",
        "code_display": "ABCD12-345678-90EFGH",
        "created_at": "2025-11-02T12:00:00"
    }
}
```

#### 2. 获取邀请码列表
```http
GET /api/admin/invitation-codes/list?status=all&page=1&per_page=20
```

**查询参数**：
- `status`: all/used/unused（默认all）
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）

#### 3. 获取邀请码详情
```http
GET /api/admin/invitation-codes/<code_id>
```

#### 4. 获取统计信息
```http
GET /api/admin/invitation-codes/statistics
```

**响应**：
```json
{
    "success": true,
    "data": {
        "total": 100,
        "used": 50,
        "unused": 50,
        "usage_rate": 50.0
    }
}
```

#### 5. 导出未使用的邀请码
```http
GET /api/admin/invitation-codes/export/unused
```

返回CSV文件。

---

### 注册API（已修改）

#### 注册新用户
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "nickname": "测试用户",
    "invitation_code": "ABCD1234567890EFGH"  // 必填
}
```

**错误响应**：
- 缺少邀请码：`INVITATION_CODE_REQUIRED`
- 邀请码无效：`INVITATION_CODE_INVALID`
- 邀请码已被使用：`CODE_ALREADY_USED`

---

## 使用测试脚本

### 运行完整测试
```bash
cd backend
source venv/bin/activate
python test_invitation_code_api.py
```

### 手动测试步骤

#### 1. 登录管理员
```bash
curl -X POST http://localhost:5002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456"}' \
  -c cookies.txt
```

#### 2. 生成单个邀请码
```bash
curl -X POST http://localhost:5002/api/admin/invitation-codes/generate \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"count":1}'
```

#### 3. 批量生成邀请码（5个）
```bash
curl -X POST http://localhost:5002/api/admin/invitation-codes/generate \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"count":5}'
```

#### 4. 获取邀请码列表
```bash
curl -X GET "http://localhost:5002/api/admin/invitation-codes/list?status=all&page=1&per_page=10" \
  -b cookies.txt
```

#### 5. 获取统计信息
```bash
curl -X GET http://localhost:5002/api/admin/invitation-codes/statistics \
  -b cookies.txt
```

#### 6. 导出未使用的邀请码
```bash
curl -X GET http://localhost:5002/api/admin/invitation-codes/export/unused \
  -b cookies.txt \
  -o invitation_codes.csv
```

#### 7. 使用邀请码注册
```bash
curl -X POST http://localhost:5002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username":"newuser",
    "email":"newuser@example.com",
    "password":"password123",
    "confirm_password":"password123",
    "invitation_code":"ABCD1234567890EFGH"
  }'
```

#### 8. 测试无效邀请码（应该失败）
```bash
curl -X POST http://localhost:5002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username":"test",
    "email":"test@example.com",
    "password":"password123",
    "confirm_password":"password123",
    "invitation_code":"INVALIDCODE123"
  }'
```

---

## 常见问题

### 1. 数据库表不存在
**错误**：`Table 'invitation_codes' doesn't exist`

**解决**：运行数据库迁移或创建表（见前置条件）

### 2. 权限不足
**错误**：`需要超级管理员权限`

**解决**：确保使用超级管理员账户登录

### 3. 邀请码格式错误
**错误**：`邀请码格式不正确`

**解决**：邀请码必须是18个字符，可以带或不带分隔符

### 4. 批量生成超过限制
**错误**：`批量生成数量不能超过10个`

**解决**：每次批量生成最多10个，分多次生成

---

## 测试检查清单

- [ ] 数据库表已创建
- [ ] 应用正在运行
- [ ] 管理员账户存在
- [ ] 可以生成单个邀请码
- [ ] 可以批量生成邀请码（限制10个）
- [ ] 可以获取邀请码列表
- [ ] 可以获取统计信息
- [ ] 可以导出未使用的邀请码
- [ ] 使用有效邀请码可以注册
- [ ] 使用无效邀请码注册失败
- [ ] 不提供邀请码注册失败
- [ ] 已使用的邀请码不能再次使用
- [ ] 普通用户不能生成邀请码

