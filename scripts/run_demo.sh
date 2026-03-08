#!/bin/bash

echo "🎓 AI School - 多Agent学习辅导系统"
echo "========================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查Python依赖..."
python3 -c "import crewai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip install -r ../backend/requirements.txt
fi

# 设置环境变量
if [ ! -f "../backend/.env" ]; then
    echo "📝 创建.env文件..."
    cp ../backend/.env.example ../backend/.env
    echo "⚠️  请编辑 backend/.env 文件设置你的API密钥"
    echo "   然后重新运行此脚本"
    exit 0
fi

# 检查API密钥
source ../backend/.env
if [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ 请先在.env文件中设置OPENAI_API_KEY"
    echo "   获取地址: https://platform.openai.com/api-keys"
    exit 1
fi

# 选择运行模式
echo ""
echo "请选择运行模式:"
echo "1. 命令行交互模式"
echo "2. Web API模式"
echo "3. Docker模式"
echo "4. 演示模式（无需API密钥）"
echo ""

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "🚀 启动命令行交互模式..."
        # 注意：现在 CLI 在 backend/cli.py
        PYTHONPATH=../backend python ../backend/cli.py
        ;;
    2)
        echo "🌐 启动Web API模式..."
        echo "API将在 http://localhost:8000 运行"
        echo "文档: http://localhost:8000/docs"
        PYTHONPATH=../backend python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    3)
        echo "🐳 启动Docker模式..."
        if ! command -v docker &> /dev/null; then
            echo "❌ 未找到Docker，请先安装Docker"
            exit 1
        fi
        
        echo "构建和启动容器..."
        # docker-compose.yml 在根目录
        docker compose -f ../docker-compose.yml up --build
        ;;
    4)
        echo "🎭 启动演示模式..."
        python run_local.py
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac