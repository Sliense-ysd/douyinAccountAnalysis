#!/bin/bash

# 抖音分析系统启动脚本

echo "🚀 启动抖音分析系统..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📍 Python版本: $python_version"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 配置文件"
    if [ -f "config.env.example" ]; then
        echo "📋 复制示例配置文件..."
        cp config.env.example .env
        echo "⚡ 请编辑 .env 文件，设置您的 TIKHUB_API_KEY"
        echo "   然后重新运行此脚本"
        exit 1
    fi
fi

# 启动应用
echo "🌟 启动应用..."
python main.py 