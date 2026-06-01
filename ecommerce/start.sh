#!/bin/bash

echo "========================================"
echo "    胖虫电商系统 - 一键启动"
echo "========================================"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "[错误] 未检测到 Docker，请先安装 Docker"
    echo "安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否可用
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "[错误] 未检测到 Docker Compose"
    exit 1
fi

echo "[信息] Docker 环境检查通过"
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo "[信息] 正在构建并启动服务..."
echo "[信息] 首次启动需要下载镜像，请耐心等待..."
echo ""

# 构建并启动所有服务
$COMPOSE_CMD up -d --build

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 启动失败，请检查错误信息"
    echo ""
    echo "常见问题排查:"
    echo "  1. 端口被占用 - 检查 5432/6379/8000/3000 端口"
    echo "  2. 内存不足 - Docker Desktop 设置中增加内存"
    echo "  3. 网络问题 - 检查网络连接或配置镜像源"
    exit 1
fi

echo ""
echo "========================================"
echo "    启动成功！"
echo "========================================"
echo ""
echo "  前端应用:     http://localhost:3000"
echo "  后端 API:     http://localhost:8000"
echo "  API 文档:     http://localhost:8000/docs"
echo "  数据库:       localhost:5432"
echo "  Redis:        localhost:6379"
echo ""
echo "  测试账号:"
echo "  普通用户:     testuser / test123456"
echo "  管理员:       admin / test123456"
echo ""
echo "========================================"
echo ""

# 询问是否打开浏览器
read -p "是否打开浏览器？(y/n): " open_browser
if [[ $open_browser =~ ^[Yy]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
        xdg-open http://localhost:8000/docs
    elif command -v open &> /dev/null; then
        open http://localhost:3000
        open http://localhost:8000/docs
    fi
fi

echo ""
echo "常用命令:"
echo "  查看日志:     $COMPOSE_CMD logs -f"
echo "  停止服务:     $COMPOSE_CMD down"
echo "  重启服务:     $COMPOSE_CMD restart"
echo "  查看状态:     $COMPOSE_CMD ps"
echo ""
