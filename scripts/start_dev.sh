#!/bin/bash
# 智策股析 - 开发环境一键启动脚本

set -e

echo "🚀 智策股析 - 开发环境启动"
echo "================================"

# 检查是否在项目根目录
if [ ! -f "prd.md" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 启动Redis（如果没有运行）
echo "📡 检查Redis服务..."
if ! pgrep -f "redis-server" > /dev/null; then
    echo "启动Redis..."
    redis-server --daemonize yes --port 6379
    sleep 2
else
    echo "✅ Redis已运行"
fi

# 启动后端
echo "🔧 启动后端服务..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 后端虚拟环境未找到，请先运行 ./scripts/setup_backend.sh"
    exit 1
fi

# 激活虚拟环境并启动
source venv/bin/activate

# 创建数据库（如果不存在）
if [ ! -f "data/dev.db" ]; then
    echo "初始化数据库..."
    python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('数据库创建完成')"
fi

echo "启动Flask应用..."
python app.py &
BACKEND_PID=$!

cd ..

# 启动前端
echo "🎨 启动前端服务..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "❌ 前端依赖未安装，请先运行 ./scripts/setup_frontend.sh"
    kill $BACKEND_PID
    exit 1
fi

echo "启动React应用..."
npm start &
FRONTEND_PID=$!

cd ..

echo ""
echo "🎉 开发环境启动完成!"
echo "================================"
echo "🔗 前端: http://localhost:3000"
echo "🔗 后端: http://localhost:5000"
echo "🔗 API文档: http://localhost:5000/api/health"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo ''; echo '停止所有服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

wait
