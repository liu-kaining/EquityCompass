#!/bin/bash
set -e

echo "🚀 智策股析 - Docker启动脚本"

# 检查是否需要初始化数据库
if [ ! -f "/app/data/.db_initialized" ]; then
    echo "📊 首次启动，初始化数据库..."
    
    # 初始化数据库结构
    python app.py init-db
    
    # 导入股票数据
    python scripts/import_stocks.py
    
    # 标记数据库已初始化
    touch /app/data/.db_initialized
    echo "✅ 数据库初始化完成"
else
    echo "✅ 数据库已初始化，跳过初始化步骤"
fi

# 启动Flask应用
echo "🌐 启动Flask应用..."
exec python app.py
