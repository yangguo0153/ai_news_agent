#!/bin/bash

# 获取脚本所在目录并进入
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================"
echo "🚀 正在启动 GEO Dashboard..."
echo "📂 工作目录: $DIR"
echo "========================================"
echo ""

# 检查 dist 目录
if [ ! -d "dist" ]; then
    echo "⚠️  未发现 dist 目录，正在构建项目..."
    if command -v npm &> /dev/null; then
        npm install && npm run build
    else
        echo "❌ 错误: 未找到 dist 目录且未安装 npm，无法构建。"
        echo "请先安装 Node.js 和 npm。"
        read -n 1 -s -r -p "按任意键退出..."
        exit 1
    fi
fi

# 自动打开浏览器
(sleep 2 && open "http://localhost:8080") &

# 启动服务器
if command -v python3 &> /dev/null; then
    echo "✅ 使用 Python 3 启动服务"
    echo "📊 访问地址: http://localhost:8080"
    echo ""
    cd dist && python3 -m http.server 8080
elif command -v python &> /dev/null; then
    echo "✅ 使用 Python 启动服务"
    echo "📊 访问地址: http://localhost:8080"
    echo ""
    cd dist && python -m SimpleHTTPServer 8080
else
    echo "⚠️  未找到 Python，尝试使用 npm preview..."
    npm run preview
fi

# 如果服务器意外退出，暂停以显示错误信息
echo ""
echo "❌ 服务器已停止"
read -n 1 -s -r -p "按任意键退出..."
