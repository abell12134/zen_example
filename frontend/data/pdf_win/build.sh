#!/bin/bash

echo "========================================"
echo "PDF处理器自动化打包脚本 (Linux)"
echo "========================================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查pip是否可用
if ! python3 -m pip --version &> /dev/null; then
    echo "错误: pip不可用，请检查Python安装"
    exit 1
fi

# 升级pip和安装构建工具
echo "升级pip和安装构建工具..."
python3 -m pip install --upgrade pip setuptools wheel

# 运行构建脚本
echo "开始构建PDF处理器..."
python3 build.py "$@"

if [ $? -eq 0 ]; then
    echo "构建成功！"
    echo "请查看packages目录中的分发包"
else
    echo "构建失败！"
    exit 1
fi