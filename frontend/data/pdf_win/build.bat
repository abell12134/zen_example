@echo off
chcp 65001 > nul
echo ========================================
echo PDF处理器自动化打包脚本 (Windows)
echo ========================================

:: 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查pip是否可用
python -m pip --version > nul 2>&1
if errorlevel 1 (
    echo 错误: pip不可用，请检查Python安装
    pause
    exit /b 1
)

:: 升级pip和安装构建工具
echo 升级pip和安装构建工具...
python -m pip install --upgrade pip setuptools wheel

:: 运行构建脚本
echo 开始构建PDF处理器...
python build.py %*

if errorlevel 1 (
    echo 构建失败！
    pause
    exit /b 1
) else (
    echo 构建成功！
    echo 请查看packages目录中的分发包
    pause
)