#!/bin/bash
set -e

echo "🚀 智策股析 - Docker启动脚本"

# 如果首次启动，则初始化数据库
if [ ! -f "/app/data/.db_initialized" ]; then
    echo "📊 首次启动，初始化数据库..."

    # 直接 Python 调用初始化
    python - <<'PY'
import os
from app import create_app, db
from app.services.data.database_service import DatabaseService

app = create_app(os.getenv("FLASK_ENV", "production"))
with app.app_context():
    db_service = DatabaseService(db.session)
    db_service.initialize_database()
    print("✅ 数据库结构初始化完成")
PY

    # 导入股票数据
    python scripts/import_stocks.py

    touch /app/data/.db_initialized
    echo "✅ 数据库初始化完成"
else
    echo "✅ 数据库已初始化，跳过初始化步骤"
fi

# 正式环境用 gunicorn 启动，避免 app.run()
echo "🌐 启动 Flask 应用..."
#exec gunicorn app:app -b 0.0.0.0:${PORT:-5002}
exec gunicorn "app:create_app()" -b 0.0.0.0:${PORT:-5002} --preload
