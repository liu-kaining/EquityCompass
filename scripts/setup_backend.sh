#!/bin/bash
# 智策股析 - 后端环境设置脚本

set -e

echo "开始设置后端开发环境..."

# 创建虚拟环境
if [ ! -d "backend/venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv backend/venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source backend/venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装Python依赖..."
pip install -r backend/requirements.txt

# 创建数据目录
echo "创建数据目录..."
mkdir -p data/{reports,exports,logs}

# 创建环境变量文件
if [ ! -f "backend/.env" ]; then
    echo "创建环境变量文件..."
    cp backend/env.example backend/.env
fi

echo "后端环境设置完成!"
echo "请运行以下命令启动后端："
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python app.py"
