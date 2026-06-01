#!/bin/bash

echo "========================================"
echo "    胖虫电商系统 - 构建镜像"
echo "========================================"
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo "[信息] 正在构建后端镜像..."
if ! docker build --network host -t pangchong-backend ./backend; then
    echo "[错误] 后端镜像构建失败"
    exit 1
fi
echo "[信息] 后端镜像构建成功"
echo ""

echo "[信息] 正在构建前端镜像..."
if ! docker build --network host -t pangchong-frontend ./frontend; then
    echo "[错误] 前端镜像构建失败"
    exit 1
fi
echo "[信息] 前端镜像构建成功"
echo ""

echo "========================================"
echo "    构建完成！"
echo "========================================"
echo ""
echo "使用 ./start.sh 启动服务"
echo ""
