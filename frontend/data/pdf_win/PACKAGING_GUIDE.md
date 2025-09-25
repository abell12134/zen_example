# PDF处理器打包部署指南

## 概述

本指南详细说明如何将 `pdf_processor_complete.py` 打包成独立的可执行文件，实现跨平台移植，特别是从Linux平台移植到Windows平台。

## 项目结构

```
pdf_process/transform/
├── pdf_processor_complete.py    # 主程序文件
├── requirements_packaging.txt   # 打包专用依赖文件
├── pdf_processor.spec          # PyInstaller配置文件
├── build.py                    # 自动化构建脚本
├── build.bat                   # Windows批处理构建脚本
├── build.sh                    # Linux shell构建脚本
├── PACKAGING_GUIDE.md          # 本文档
├── build/                      # 构建临时目录
├── dist/                       # 输出目录
└── packages/                   # 最终分发包目录
```

## 依赖分析

### 核心依赖
- **PyMuPDF (fitz)**: PDF文档处理
- **openpyxl**: Excel文件操作
- **Pillow (PIL)**: 图像处理
- **rapidocr-onnxruntime**: OCR文字识别
- **tkinter**: GUI界面（Python标准库）

### 打包工具
- **PyInstaller**: 将Python脚本打包成可执行文件

## 快速开始

### 方法一：使用自动化脚本（推荐）

#### Windows平台
```batch
# 双击运行或在命令行执行
build.bat

# 或者带参数运行
build.bat --debug
```

#### Linux平台
```bash
# 给脚本执行权限
chmod +x build.sh

# 运行构建脚本
./build.sh

# 或者带参数运行
./build.sh --debug
```

### 方法二：使用Python构建脚本

```bash
# 安装依赖
pip install -r requirements_packaging.txt

# 运行构建脚本
python build.py

# 查看帮助
python build.py --help
```

### 方法三：手动构建

```bash
# 1. 安装依赖
pip install -r requirements_packaging.txt

# 2. 清理旧的构建文件
rm -rf build dist

# 3. 使用PyInstaller打包
pyinstaller --clean pdf_processor.spec

# 4. 查看输出
ls dist/
```

## 构建选项

### 构建脚本参数

```bash
python build.py [选项]

选项:
  --no-clean      不清理构建目录
  --no-deps       不安装依赖包
  --debug         启用调试模式
  --no-test       不测试可执行文件
  --project-dir   指定项目目录路径
```

### PyInstaller配置说明

`pdf_processor.spec` 文件包含以下关键配置：

- **hiddenimports**: 显式导入可能被遗漏的模块
- **datas**: 包含OCR模型文件和配置文件
- **excludes**: 排除不需要的大型库以减小文件大小
- **upx**: 启用压缩以减小可执行文件大小

## 跨平台部署

### Windows部署

1. **系统要求**
   - Windows 7/8/10/11 (64位)
   - 无需安装Python环境

2. **部署步骤**
   ```
   1. 解压分发包到目标目录
   2. 双击 pdf_processor.exe 或运行批处理脚本
   3. 首次运行会初始化OCR模型（需要网络连接）
   ```

3. **使用方式**
   ```batch
   # 命令行模式
   pdf_processor.exe input.pdf
   pdf_processor.exe input.pdf --output output_dir
   
   # GUI模式
   pdf_processor.exe --gui
   
   # 或双击 start_gui.bat
   ```

### Linux部署

1. **系统要求**
   - Linux发行版（Ubuntu 18.04+, CentOS 7+等）
   - 64位系统
   - 无需安装Python环境

2. **部署步骤**
   ```bash
   # 解压分发包
   unzip pdf_processor_linux_*.zip
   cd pdf_processor_linux_*
   
   # 给执行权限
   chmod +x pdf_processor
   chmod +x *.sh
   
   # 运行程序
   ./pdf_processor --help
   ```

## 常见问题解决

### 1. OCR模型加载失败

**问题**: 程序启动时提示OCR模型加载失败

**解决方案**:
```bash
# 确保网络连接正常，首次运行会下载模型
# 或手动下载模型文件到程序目录
```

### 2. 可执行文件过大

**问题**: 生成的exe文件超过500MB

**解决方案**:
```python
# 在spec文件中添加更多排除项
excludes = [
    'matplotlib', 'scipy', 'pandas', 'jupyter',
    'IPython', 'notebook', 'pytest', 'setuptools'
]
```

### 3. 缺少DLL文件（Windows）

**问题**: Windows上运行时提示缺少DLL

**解决方案**:
```bash
# 安装Visual C++ Redistributable
# 或在spec文件中添加binaries配置
```

### 4. 权限问题（Linux）

**问题**: Linux上无法执行程序

**解决方案**:
```bash
chmod +x pdf_processor
# 确保当前用户有执行权限
```

### 5. 中文字符显示问题

**问题**: 中文路径或文件名显示乱码

**解决方案**:
```python
# 确保系统编码设置正确
# Windows: chcp 65001
# Linux: export LANG=zh_CN.UTF-8
```

## 性能优化

### 1. 减小文件大小

```python
# 在spec文件中优化配置
excludes = ['test', 'tests', 'unittest', 'doctest']
upx = True  # 启用UPX压缩
```

### 2. 提高启动速度

```python
# 使用--onefile模式可能较慢，考虑使用--onedir
# 预加载常用模块
```

### 3. 内存优化

```python
# 处理大文件时分批处理
# 及时释放不需要的对象
```

## 高级配置

### 自定义图标

```python
# 在spec文件中添加图标
exe = EXE(
    # ... 其他配置
    icon='icon.ico'  # Windows图标文件
)
```

### 添加版本信息

```python
# 创建version.txt文件
# 在spec文件中引用版本信息
```

### 数字签名（Windows）

```bash
# 使用signtool对exe文件进行数字签名
signtool sign /f certificate.pfx /p password pdf_processor.exe
```

## 测试验证

### 功能测试

```bash
# 测试命令行功能
./pdf_processor --help
./pdf_processor sample.pdf

# 测试GUI功能
./pdf_processor --gui
```

### 性能测试

```bash
# 测试大文件处理
time ./pdf_processor large_file.pdf

# 测试内存使用
top -p $(pgrep pdf_processor)
```

## 分发建议

### 1. 创建安装包

- Windows: 使用NSIS或Inno Setup创建安装程序
- Linux: 创建AppImage或deb/rpm包

### 2. 版本管理

```
pdf_processor_v1.0.0_windows_x64.zip
pdf_processor_v1.0.0_linux_x64.tar.gz
```

### 3. 文档完善

- 用户手册
- 快速入门指南
- 常见问题FAQ

## 技术支持

如遇到问题，请按以下步骤排查：

1. 检查系统要求是否满足
2. 查看控制台错误输出
3. 检查文件权限设置
4. 验证输入文件格式
5. 查看日志文件（如果有）

## 更新日志

### v1.0.0
- 初始版本
- 支持PDF文本提取和OCR
- 支持Excel导出
- 跨平台支持

---

**注意**: 本文档会随着项目更新而持续维护，请关注最新版本。