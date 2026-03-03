#!/usr/bin/env bash
set -e

PROJECT_NAME="AISchool"
COMPOSE_FILE="docker-compose.yml"

# 自动检测 docker compose 命令
if docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "[错误] docker compose 不可用，请升级 Docker 或安装 docker-compose"
    exit 1
fi

usage() {
    echo ""
    echo "🎓 ${PROJECT_NAME} - Docker 管理脚本"
    echo "============================================"
    echo "用法: ./manage.sh [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start            构建并后台启动所有服务"
    echo "  stop             停止并移除所有容器"
    echo "  restart          重启所有服务"
    echo "  status           查看容器运行状态"
    echo "  logs [service]   查看日志（可选指定服务：backend / db / redis）"
    echo "  build            重新构建镜像（不启动）"
    echo "  help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./manage.sh start"
    echo "  ./manage.sh logs backend"
    echo "  ./manage.sh stop"
    echo ""
}

check_docker() {
    if ! docker --version &>/dev/null; then
        echo "[错误] Docker 未安装或未运行，请先启动 Docker"
        exit 1
    fi
}

cmd_start() {
    check_docker
    echo "🚀 启动所有服务 (${PROJECT_NAME})..."
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            echo "⚠️  未检测到 .env 文件，正在从 .env.example 复制..."
            cp .env.example .env
            echo "⚠️  请编辑 .env 文件配置 API 密钥后重新运行"
            exit 0
        else
            echo "[错误] 缺少 .env 文件，无法启动"
            exit 1
        fi
    fi
    $COMPOSE_CMD -f "$COMPOSE_FILE" up --build -d
    echo ""
    echo "✅ 所有服务已启动！"
    echo "   后端 API : http://localhost:8000"
    echo "   API 文档 : http://localhost:8000/docs"
    echo "   PostgreSQL: localhost:5432"
    echo "   Redis     : localhost:6379"
    echo ""
    echo "提示: 使用 ./manage.sh logs backend 查看后端日志"
}

cmd_stop() {
    check_docker
    echo "🛑 停止所有服务..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" down
    echo "✅ 所有服务已停止"
}

cmd_restart() {
    check_docker
    echo "🔄 重启所有服务..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" down
    $COMPOSE_CMD -f "$COMPOSE_FILE" up --build -d
    echo "✅ 所有服务已重启"
}

cmd_status() {
    check_docker
    echo "📊 当前服务状态："
    echo ""
    $COMPOSE_CMD -f "$COMPOSE_FILE" ps
}

cmd_logs() {
    check_docker
    if [ -z "$1" ]; then
        echo "📋 显示所有服务日志 (Ctrl+C 退出)..."
        $COMPOSE_CMD -f "$COMPOSE_FILE" logs -f
    else
        echo "📋 显示 $1 日志 (Ctrl+C 退出)..."
        $COMPOSE_CMD -f "$COMPOSE_FILE" logs -f "$1"
    fi
}

cmd_build() {
    check_docker
    echo "🔨 重新构建镜像..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" build --no-cache
    echo "✅ 构建完成"
}

case "$1" in
    start)   cmd_start ;;
    stop)    cmd_stop ;;
    restart) cmd_restart ;;
    status)  cmd_status ;;
    logs)    cmd_logs "$2" ;;
    build)   cmd_build ;;
    help|-h|--help) usage ;;
    "")      usage ;;
    *)
        echo "[错误] 未知命令: $1"
        usage
        exit 1
        ;;
esac
