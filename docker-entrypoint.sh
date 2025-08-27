#!/bin/bash
set -e

echo "🚀 智策股析 - Docker启动脚本"

# 如果首次启动，则初始化数据库
if [ ! -f "/app/data/.db_initialized" ]; then
    echo "📊 首次启动，初始化数据库..."

    # 直接 Python 调用初始化
    python - <<'PY'
import os
import sys

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///dev.db')

print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.path}")

try:
    from app import create_app, db
    from app.services.data.database_service import DatabaseService
    
    app = create_app(os.getenv("FLASK_ENV", "production"))
    with app.app_context():
        try:
            # 确保所有模型都被导入
            from app.models import (
                User, UserPlan, Stock, UserWatchlist, AnalysisTask, 
                PromptTemplate, ReportIndex, EmailSubscription, 
                PaymentTransaction, Admin, SystemConfig
            )
            print("✅ 模型导入完成")
            
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建完成")
            
            # 初始化数据
            db_service = DatabaseService(db.session)
            db_service.initialize_database()
            print("✅ 数据库结构初始化完成")
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
except Exception as e:
    print(f"❌ 应用导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PY

    # 导入股票数据
    echo "📈 开始导入股票数据..."
    cd /app && python scripts/import_stocks.py || {
        echo "⚠️ 股票数据导入失败，但继续启动应用"
    }

    touch /app/data/.db_initialized
    echo "✅ 数据库初始化完成"
else
    echo "✅ 数据库已初始化，跳过初始化步骤"
fi

# 正式环境用 gunicorn 启动，避免 app.run()
echo "🌐 启动 Flask 应用..."
exec gunicorn "app:app" -b 0.0.0.0:${PORT:-5002} --preload --chdir /app
