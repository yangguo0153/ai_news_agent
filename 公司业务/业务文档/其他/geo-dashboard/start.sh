#!/bin/bash
# GEO Dashboard 一键启动脚本
# 使用方法：双击此文件或在终端运行 ./start.sh

cd "$(dirname "$0")"

echo "🚀 正在启动 GEO 效果监测看板..."
echo ""

# 检查是否有Python可用
if command -v python3 &> /dev/null; then
    echo "📊 Dashboard 地址: http://localhost:8080"
    echo "⏹️  按 Ctrl+C 停止服务器"
    echo ""
    cd dist && python3 -m http.server 8080
elif command -v python &> /dev/null; then
    echo "📊 Dashboard 地址: http://localhost:8080"
    echo "⏹️  按 Ctrl+C 停止服务器"
    echo ""
    cd dist && python -m SimpleHTTPServer 8080
else
    echo "❌ 未找到 Python，尝试使用 npm 开发服务器..."
    npm run dev
fi
