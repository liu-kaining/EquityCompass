#!/bin/bash
# 智策股析 - 前端环境设置脚本

set -e

echo "开始设置前端开发环境..."

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 请先安装Node.js"
    echo "访问 https://nodejs.org/ 下载安装"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "错误: npm未找到"
    exit 1
fi

echo "Node.js版本: $(node --version)"
echo "npm版本: $(npm --version)"

# 安装依赖
echo "安装前端依赖..."
cd frontend
npm install

# 创建环境变量文件
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp env.example .env
fi

echo "前端环境设置完成!"
echo "请运行以下命令启动前端："
echo "  cd frontend"
echo "  npm start"
