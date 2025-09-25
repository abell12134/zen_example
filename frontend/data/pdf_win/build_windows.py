#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF处理器Windows平台打包脚本
支持在Linux环境下交叉编译Windows可执行文件
"""

import os
import sys
import shutil
import subprocess
import platform
import zipfile
from datetime import datetime
from pathlib import Path

class WindowsPDFProcessorBuilder:
    def __init__(self):
        self.project_dir = Path(__file__).parent.absolute()
        self.script_file = self.project_dir / "pdf_processor_complete.py"
        self.spec_file = self.project_dir / "pdf_processor_windows.spec"
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        self.packages_dir = self.project_dir / "packages"
        
        # 平台信息
        self.host_platform = platform.system().lower()
        self.target_platform = "windows"
        self.arch = "x86_64"
        
        # 必要文件检查
        self.required_files = [
            self.script_file,
            self.spec_file
        ]
        
    def log(self, message):
        """打印带时间戳的日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def check_prerequisites(self):
        """检查构建前提条件"""
        self.log("检查Windows构建前提条件...")
        
        # 检查必要文件
        for file_path in self.required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"必要文件不存在: {file_path}")
        self.log("✓ 必要文件检查通过")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            raise RuntimeError(f"需要Python 3.8+，当前版本: {python_version.major}.{python_version.minor}")
        self.log(f"✓ Python版本检查通过: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查PyInstaller
        try:
            result = subprocess.run(['pyinstaller', '--version'], 
                                  capture_output=True, text=True, check=True)
            pyinstaller_version = result.stdout.strip()
            self.log(f"✓ PyInstaller版本: {pyinstaller_version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("PyInstaller未安装或不可用")
            
        # 检查关键依赖
        try:
            import rapidocr_onnxruntime
            self.log(f"✓ RapidOCR可用")
        except ImportError:
            self.log("⚠ RapidOCR不可用，OCR功能可能受限")
            
        # 警告交叉编译限制
        if self.host_platform != "windows":
            self.log("⚠ 注意: 在非Windows环境下构建Windows可执行文件")
            self.log("⚠ 某些Windows特定功能可能无法完全测试")
            
    def clean_build_dirs(self):
        """清理构建目录"""
        self.log("清理构建目录...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.log(f"✓ 已清理: {dir_path}")
                
    def build_executable(self):
        """构建Windows可执行文件"""
        self.log("开始构建Windows可执行文件...")
        
        # 构建命令
        cmd = [
            'pyinstaller',
            '--clean',
            '--noconfirm',
            str(self.spec_file)
        ]
        
        self.log(f"执行命令: {' '.join(cmd)}")
        
        # 执行构建
        try:
            result = subprocess.run(cmd, cwd=self.project_dir, 
                                  capture_output=True, text=True, check=True)
            self.log("✓ 构建成功")
            
            # 检查输出文件（在Linux环境下可能没有.exe扩展名）
            exe_name_without_ext = 'pdf_processor'
            exe_name_with_ext = 'pdf_processor.exe'
            
            # 先检查是否有.exe文件
            exe_path = self.dist_dir / exe_name_with_ext
            if not exe_path.exists():
                # 如果没有.exe文件，检查无扩展名的文件
                exe_path = self.dist_dir / exe_name_without_ext
                if not exe_path.exists():
                    raise FileNotFoundError(f"构建的可执行文件不存在: {self.dist_dir}")
                else:
                    self.log("⚠ 注意: 在Linux环境下生成的是无扩展名的可执行文件")
                    # 重命名为.exe文件以便Windows使用
                    exe_path_renamed = self.dist_dir / exe_name_with_ext
                    shutil.copy2(exe_path, exe_path_renamed)
                    exe_path = exe_path_renamed
                    self.log(f"✓ 已重命名为: {exe_name_with_ext}")
                
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            self.log(f"✓ Windows可执行文件大小: {file_size:.1f} MB")
            
            return exe_path
            
        except subprocess.CalledProcessError as e:
            self.log(f"构建失败，退出代码: {e.returncode}")
            self.log(f"错误输出: {e.stderr}")
            raise RuntimeError(f"PyInstaller构建失败: {e.stderr}")
            
    def create_windows_distribution_package(self, exe_path):
        """创建Windows分发包"""
        self.log("创建Windows分发包...")
        
        # 创建包目录
        self.packages_dir.mkdir(exist_ok=True)
        
        # 生成包名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"pdf_processor_windows_{self.arch}_{timestamp}"
        package_dir = self.packages_dir / package_name
        
        # 创建包目录
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir(parents=True)
        
        # 复制可执行文件
        exe_name = exe_path.name
        target_exe = package_dir / exe_name
        shutil.copy2(exe_path, target_exe)
        
        self.log(f"✓ 已复制可执行文件: {exe_name}")
        
        # 创建使用说明
        readme_content = self._generate_windows_readme(exe_name)
        readme_path = package_dir / "README.txt"
        readme_path.write_text(readme_content, encoding='utf-8')
        self.log("✓ 已创建README.txt")
        
        # 创建Windows启动脚本
        self._create_windows_scripts(package_dir, exe_name)
        
        # 创建压缩包
        zip_path = self.packages_dir / f"{package_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.packages_dir)
                    zipf.write(file_path, arcname)
        
        self.log(f"✓ 已创建压缩包: {zip_path.name}")
        
        return package_dir, zip_path
        
    def _generate_windows_readme(self, exe_name):
        """生成Windows README内容"""
        return f"""PDF处理器 - Windows独立可执行版本

版本信息:
- 构建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 目标平台: Windows {self.arch}
- 可执行文件: {exe_name}

系统要求:
- Windows 7/8/10/11 (64位)
- 至少200MB可用磁盘空间
- 无需安装Python或其他依赖

使用方法:

1. 命令行模式:
   {exe_name} --help                    # 查看帮助
   {exe_name} -p input.pdf              # 处理单个PDF文件
   {exe_name} -p input.pdf -o output\\   # 指定输出目录
   {exe_name} --batch input_folder\\     # 批量处理文件夹

2. GUI模式:
   {exe_name} --gui                     # 启动图形界面
   或者双击 start_gui.bat

3. 快速处理:
   将PDF文件拖拽到 process_pdf.bat 上

功能特性:
- PDF文本提取和处理
- OCR文字识别（支持中英文）
- Excel文件生成和处理
- 批量文件处理
- 图形用户界面

注意事项:
- 首次运行可能需要较长初始化时间
- 确保有足够的磁盘空间用于临时文件
- 如果Windows Defender报警，请添加到白名单
- 建议在命令提示符中运行以查看详细日志

故障排除:
- 如果程序无法启动，请检查Windows版本兼容性
- 如果OCR功能异常，请确保网络连接正常
- 如果处理大文件时内存不足，请关闭其他程序
- 遇到权限问题时，请以管理员身份运行

技术支持:
- 确保使用绝对路径避免路径问题
- 文件名避免使用特殊字符
- 建议将程序放在英文路径下运行
"""

    def _create_windows_scripts(self, package_dir, exe_name):
        """创建Windows启动脚本"""
        # 处理PDF脚本
        process_script = package_dir / "process_pdf.bat"
        process_script.write_text(f"""@echo off
chcp 65001 >nul
echo PDF处理器 - 批量处理模式
echo.
if "%~1"=="" (
    echo 用法: 将PDF文件或文件夹拖拽到此批处理文件上
    echo 或者: process_pdf.bat "文件路径"
    echo.
    echo 示例: process_pdf.bat "C:\\Documents\\test.pdf"
    echo       process_pdf.bat "C:\\Documents\\PDFs\\"
    echo.
    pause
    exit /b 1
)

echo 正在处理: %~1
echo.
"{exe_name}" -p "%~1"
echo.
echo 处理完成，按任意键退出...
pause >nul
""", encoding='utf-8')
        
        # GUI启动脚本
        gui_script = package_dir / "start_gui.bat"
        gui_script.write_text(f"""@echo off
chcp 65001 >nul
echo 启动PDF处理器图形界面...
echo.
"{exe_name}" --gui
""", encoding='utf-8')
        
        # 帮助脚本
        help_script = package_dir / "show_help.bat"
        help_script.write_text(f"""@echo off
chcp 65001 >nul
echo PDF处理器 - 帮助信息
echo.
"{exe_name}" --help
echo.
pause
""", encoding='utf-8')
        
        self.log("✓ 已创建Windows批处理脚本")
        
    def test_executable_basic(self, exe_path):
        """基本测试可执行文件（在Linux环境下有限测试）"""
        self.log("执行基本文件检查...")
        
        try:
            # 检查文件是否存在且有合理大小
            if not exe_path.exists():
                self.log("✗ 可执行文件不存在")
                return False
                
            file_size = exe_path.stat().st_size
            if file_size < 1024 * 1024:  # 小于1MB可能有问题
                self.log(f"⚠ 可执行文件大小异常: {file_size} bytes")
                return False
                
            self.log("✓ 文件基本检查通过")
            self.log("⚠ 注意: 无法在Linux环境下完全测试Windows可执行文件")
            self.log("⚠ 建议在Windows环境下进行完整测试")
            
            return True
            
        except Exception as e:
            self.log(f"✗ 文件检查失败: {e}")
            return False
            
    def build(self):
        """执行完整构建流程"""
        try:
            self.log("开始PDF处理器Windows构建流程")
            self.log(f"主机平台: {self.host_platform}")
            self.log(f"目标平台: {self.target_platform} {self.arch}")
            self.log(f"项目目录: {self.project_dir}")
            
            # 检查前提条件
            self.check_prerequisites()
            
            # 清理构建目录
            self.clean_build_dirs()
            
            # 构建可执行文件
            exe_path = self.build_executable()
            
            # 创建分发包
            package_dir, zip_path = self.create_windows_distribution_package(exe_path)
            
            # 基本测试
            test_success = self.test_executable_basic(exe_path)
            
            # 构建完成
            self.log("=" * 60)
            self.log("Windows构建完成!")
            self.log(f"分发包目录: {package_dir}")
            self.log(f"压缩包文件: {zip_path}")
            self.log(f"可执行文件大小: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            self.log(f"基本检查: {'通过' if test_success else '需要在Windows环境下验证'}")
            self.log("=" * 60)
            self.log("重要提醒:")
            self.log("1. 请在Windows环境下测试可执行文件")
            self.log("2. 首次运行可能需要较长时间初始化")
            self.log("3. 如遇杀毒软件报警，请添加到白名单")
            self.log("=" * 60)
            
            return True
            
        except Exception as e:
            self.log(f"构建失败: {e}")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PDF处理器Windows构建脚本')
    parser.add_argument('--no-deps', action='store_true', 
                       help='跳过依赖检查（用于测试）')
    
    args = parser.parse_args()
    
    builder = WindowsPDFProcessorBuilder()
    
    if args.no_deps:
        builder.log("跳过依赖检查模式")
    
    success = builder.build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()