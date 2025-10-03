# 金币系统迁移指南

## 概述

本指南详细说明了如何从无金币版本迁移到金币版本，确保现有用户和数据的安全迁移。

## 迁移前准备

### 1. 环境检查

```bash
# 确保在正确的目录
cd /path/to/EquityCompass/backend

# 检查Python环境
python --version
pip list | grep -E "(flask|sqlalchemy)"

# 检查数据库文件
ls -la instance/equitycompass.db
```

### 2. 数据备份

**重要：在开始迁移前，必须创建完整的数据备份！**

```bash
# 创建备份目录
mkdir -p backups

# 备份数据库
cp instance/equitycompass.db backups/equitycompass_backup_$(date +%Y%m%d_%H%M%S).db

# 备份整个项目（可选）
tar -czf backups/project_backup_$(date +%Y%m%d_%H%M%S).tar.gz ../
```

## 迁移步骤

### 步骤1：试运行迁移

首先进行试运行，检查迁移过程：

```bash
python scripts/migrate_to_coin_system.py --dry-run
```

这将显示迁移计划，但不会实际修改数据。

### 步骤2：创建金币系统表

```bash
python scripts/create_coin_tables.py
```

### 步骤3：执行正式迁移

```bash
python scripts/migrate_to_coin_system.py
```

### 步骤4：验证迁移结果

迁移完成后，验证以下内容：

1. **检查用户金币账户**
```bash
python -c "
from app import create_app, db
from app.models.user import User
from app.models.coin import UserCoin

app = create_app()
with app.app_context():
    users = User.query.filter_by(is_active=True).all()
    for user in users:
        coin = UserCoin.query.filter_by(user_id=user.id).first()
        if coin:
            print(f'用户 {user.username}: {coin.available_coins} 金币')
        else:
            print(f'用户 {user.username}: 无金币账户')
"
```

2. **检查金币套餐**
```bash
python -c "
from app import create_app, db
from app.models.coin import CoinPackage

app = create_app()
with app.app_context():
    packages = CoinPackage.query.all()
    print(f'金币套餐数量: {len(packages)}')
    for pkg in packages:
        print(f'  {pkg.name}: {pkg.coins}金币 - ¥{pkg.price}')
"
```

3. **检查交易记录**
```bash
python -c "
from app import create_app, db
from app.models.coin import CoinTransaction

app = create_app()
with app.app_context():
    transactions = CoinTransaction.query.count()
    print(f'交易记录数量: {transactions}')
"
```

## 金币分配策略

### 基础金币
- 所有用户：20金币（可分析2个报告）

### 角色奖励
- 超级管理员：+1000金币
- 站点管理员：+500金币
- 普通用户：+0金币

### 老用户奖励
- 注册超过30天：+50金币
- 注册超过7天：+20金币

### 历史使用奖励
- 每个历史分析任务：+5金币（最多100金币）

## 回滚方案

如果迁移过程中出现问题，可以使用回滚脚本：

### 1. 仅清理金币数据
```bash
python scripts/rollback_coin_system.py
```

### 2. 恢复完整数据库备份
```bash
python scripts/rollback_coin_system.py --backup-file backups/equitycompass_backup_YYYYMMDD_HHMMSS.db
```

## 迁移后配置

### 1. 更新应用配置

确保以下配置正确：

```python
# app/config/settings.py
COIN_SYSTEM_ENABLED = True
DEFAULT_COINS_PER_ANALYSIS = 10
DAILY_BONUS_BASE_COINS = 20
```

### 2. 测试关键功能

```bash
# 测试用户登录
curl -X POST http://localhost:5002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password"}'

# 测试金币信息
curl -b cookies.txt http://localhost:5002/api/coin/info

# 测试每日签到
curl -b cookies.txt -X POST http://localhost:5002/api/coin/daily-bonus

# 测试股票分析
curl -b cookies.txt -X POST http://localhost:5002/api/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "AAPL", "analysis_type": "technical"}'
```

## 常见问题

### Q1: 迁移过程中断怎么办？
A: 使用回滚脚本清理部分数据，然后重新开始迁移。

### Q2: 用户金币数量不对怎么办？
A: 可以手动调整用户金币：
```python
from app import create_app, db
from app.models.coin import UserCoin

app = create_app()
with app.app_context():
    user_coin = UserCoin.query.filter_by(user_id=USER_ID).first()
    if user_coin:
        user_coin.available_coins = NEW_AMOUNT
        user_coin.total_coins = NEW_AMOUNT
        db.session.commit()
```

### Q3: 如何为特定用户添加金币？
A: 使用金币服务：
```python
from app import create_app, db
from app.services.coin.coin_service import CoinService

app = create_app()
with app.app_context():
    coin_service = CoinService(db.session)
    result = coin_service.earn_coins(
        user_id=USER_ID,
        amount=AMOUNT,
        description="手动调整",
        transaction_type='ADMIN_ADJUST'
    )
```

## 监控和维护

### 1. 定期检查
- 监控金币交易记录
- 检查异常的金币消耗
- 验证每日签到功能

### 2. 数据清理
- 定期清理过期的交易记录
- 归档历史数据

### 3. 性能优化
- 为金币相关表添加索引
- 优化查询性能

## 联系支持

如果在迁移过程中遇到问题，请：

1. 检查迁移日志文件
2. 查看应用日志
3. 联系技术支持团队

---

**重要提醒**：
- 迁移前务必备份数据
- 在生产环境迁移前，先在测试环境验证
- 迁移过程中保持应用离线状态
- 迁移完成后进行充分的功能测试
