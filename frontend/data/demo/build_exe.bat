@echo off
chcp 65001 >nul
echo ================================================
echo PDF处理工具 - Windows可执行程序打包脚本
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查是否在正确目录
if not exist "pdf_processor_complete.py" (
    echo 错误: 未找到pdf_processor_complete.py文件
    echo 请确保在正确的目录下运行此脚本
    pause
    exit /b 1
)

echo 检查并安装PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo PyInstaller安装失败
        pause
        exit /b 1
    )
    echo PyInstaller安装成功
) else (
    echo PyInstaller已安装
)

echo.
echo 选择构建方式:
echo 1. 单文件模式（推荐）- 生成单个exe文件
echo 2. 目录模式 - 生成包含依赖的文件夹
echo 3. 使用自定义规格文件
echo.
set /p choice="请选择 (1/2/3，默认为1): "
if "%choice%"=="" set choice=1

REM 清理之前的构建
if exist "build" (
    echo 清理build目录...
    rmdir /s /q "build"
)
if exist "dist" (
    echo 清理dist目录...
    rmdir /s /q "dist"
)

echo.
echo 开始构建...

if "%choice%"=="1" (
    echo 使用单文件模式构建...
    pyinstaller --onefile --windowed --name="PDF处理工具" --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox --hidden-import=rapidocr_onnxruntime --hidden-import=openpyxl --hidden-import=fitz --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageTk --hidden-import=numpy --hidden-import=cv2 pdf_processor_complete.py
) else if "%choice%"=="2" (
    echo 使用目录模式构建...
    pyinstaller --windowed --name="PDF处理工具" --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox --hidden-import=rapidocr_onnxruntime --hidden-import=openpyxl --hidden-import=fitz --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageTk --hidden-import=numpy --hidden-import=cv2 pdf_processor_complete.py
) else if "%choice%"=="3" (
    echo 使用自定义规格文件构建...
    if not exist "pdf_processor.spec" (
        echo 创建规格文件...
        python build_exe.py
    ) else (
        echo 使用现有规格文件...
        pyinstaller pdf_processor.spec
    )
) else (
    echo 无效选择，使用默认单文件模式
    pyinstaller --onefile --windowed --name="PDF处理工具" --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox --hidden-import=rapidocr_onnxruntime --hidden-import=openpyxl --hidden-import=fitz --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageTk --hidden-import=numpy --hidden-import=cv2 pdf_processor_complete.py
)

if errorlevel 1 (
    echo.
    echo 构建失败！请检查错误信息
    pause
    exit /b 1
)

echo.
echo ================================================
echo 构建完成！
echo ================================================

if exist "dist\PDF处理工具.exe" (
    echo 可执行文件已生成: dist\PDF处理工具.exe
    
    REM 获取文件大小
    for %%A in ("dist\PDF处理工具.exe") do (
        set size=%%~zA
        set /a sizeMB=!size!/1024/1024
        echo 文件大小: !sizeMB! MB
    )
    
    echo.
    echo 使用说明:
    echo 1. 将dist目录中的文件复制到目标Windows系统
    echo 2. 双击PDF处理工具.exe运行程序
    echo 3. 程序支持GUI界面和命令行两种模式
    echo.
    
    set /p open="是否打开dist目录? (y/n): "
    if /i "%open%"=="y" (
        explorer dist
    )
) else (
    echo 警告: 未找到生成的可执行文件
    if exist "dist" (
        echo 请检查dist目录中的文件
        dir dist
    )
)

echo.
echo 按任意键退出...
pause >nul