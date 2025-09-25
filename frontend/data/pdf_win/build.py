#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF处理器自动化打包脚本
优化版本，解决OCR模型加载问题
支持Windows和Linux平台的自动化打包
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
import zipfile
from pathlib import Path
from datetime import datetime


class PDFProcessorBuilder:
    """PDF处理器打包构建器"""
    
    def __init__(self, project_dir=None):
        """初始化构建器
        
        Args:
            project_dir: 项目目录，默认为当前脚本所在目录
        """
        self.project_dir = Path(project_dir) if project_dir else Path(__file__).parent.absolute()
        self.script_file = self.project_dir / "pdf_processor_complete.py"
        self.spec_file = self.project_dir / "pdf_processor.spec"
        self.requirements_file = self.project_dir / 'requirements_packaging.txt'
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        self.packages_dir = self.project_dir / "packages"
        
        # 平台信息
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()
        
        print(f"构建平台: {self.platform} ({self.arch})")
        print(f"项目目录: {self.project_dir}")
    
    def check_prerequisites(self):
        """检查构建前提条件"""
        print("\n=== 检查构建前提条件 ===")
        
        # 检查必要文件
        required_files = [self.script_file, self.spec_file, self.requirements_file]
        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"必需文件不存在: {file_path}")
            print(f"✓ 找到文件: {file_path.name}")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            raise RuntimeError(f"需要Python 3.8+，当前版本: {python_version.major}.{python_version.minor}")
        print(f"✓ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查PyInstaller
        try:
            result = subprocess.run(['pyinstaller', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✓ PyInstaller版本: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("PyInstaller未安装或不可用")
    
    def install_dependencies(self, force=False):
        """安装依赖包
        
        Args:
            force: 是否强制重新安装
        """
        print("\n=== 安装依赖包 ===")
        
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(self.requirements_file)]
        if force:
            cmd.append('--force-reinstall')
        
        try:
            subprocess.run(cmd, check=True)
            print("✓ 依赖包安装完成")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"依赖包安装失败: {e}")
    
    def clean_build_dirs(self):
        """清理构建目录"""
        print("\n=== 清理构建目录 ===")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"✓ 清理目录: {dir_path}")
        
        # 清理__pycache__
        for pycache in self.project_dir.rglob('__pycache__'):
            if pycache.is_dir():
                shutil.rmtree(pycache)
                print(f"✓ 清理缓存: {pycache}")
    
    def build_executable(self, debug=False):
        """构建可执行文件
        
        Args:
            debug: 是否启用调试模式
        """
        print("\n=== 构建可执行文件 ===")
        
        # 构建命令
        cmd = ['pyinstaller', '--clean']
        
        if debug:
            cmd.append('--debug=all')
        
        cmd.append(str(self.spec_file))
        
        # 执行构建
        try:
            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=self.project_dir, check=True, 
                                  capture_output=True, text=True)
            print("✓ 构建完成")
            
            if result.stdout:
                print("构建输出:")
                print(result.stdout)
                
        except subprocess.CalledProcessError as e:
            print(f"构建失败: {e}")
            if e.stdout:
                print("标准输出:")
                print(e.stdout)
            if e.stderr:
                print("错误输出:")
                print(e.stderr)
            raise
    
    def create_distribution_package(self):
        """创建分发包"""
        print("\n=== 创建分发包 ===")
        
        # 确定可执行文件路径
        exe_name = 'pdf_processor'
        if self.platform == 'windows':
            exe_name += '.exe'
        
        exe_path = self.dist_dir / exe_name
        if not exe_path.exists():
            raise FileNotFoundError(f"可执行文件不存在: {exe_path}")
        
        # 创建分发目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        package_name = f'pdf_processor_{self.platform}_{self.arch}_{timestamp}'
        package_dir = self.project_dir / 'packages' / package_name
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制可执行文件
        shutil.copy2(exe_path, package_dir / exe_name)
        print(f"✓ 复制可执行文件: {exe_name}")
        
        # 创建使用说明
        readme_content = self._generate_readme(exe_name)
        readme_path = package_dir / 'README.txt'
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"✓ 创建使用说明: README.txt")
        
        # 创建示例脚本
        if self.platform == 'windows':
            self._create_windows_scripts(package_dir, exe_name)
        else:
            self._create_linux_scripts(package_dir, exe_name)
        
        # 创建压缩包
        archive_path = self.project_dir / 'packages' / f'{package_name}.zip'
        shutil.make_archive(str(archive_path.with_suffix('')), 'zip', package_dir)
        print(f"✓ 创建压缩包: {archive_path.name}")
        
        return package_dir, archive_path
    
    def _generate_readme(self, exe_name):
        """生成README文件内容"""
        return f"""PDF处理器 - 独立可执行版本
================================

版本信息:
- 构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 构建平台: {self.platform} ({self.arch})
- 可执行文件: {exe_name}

使用方法:
1. 命令行模式:
   {exe_name} --help                    # 查看帮助
   {exe_name} input.pdf                 # 处理单个PDF文件
   {exe_name} input.pdf --output dir    # 指定输出目录
   
2. GUI模式:
   {exe_name} --gui                     # 启动图形界面

功能特性:
- PDF文本提取和OCR识别
- 支持中英文文本识别
- 导出到Excel格式
- 图片提取和处理
- 跨平台支持

注意事项:
- 首次运行可能需要较长时间初始化OCR模型
- 确保有足够的磁盘空间用于临时文件
- 大文件处理时请耐心等待

技术支持:
如遇问题，请检查以下事项:
1. 确保输入文件路径正确
2. 检查文件权限
3. 确保有足够的内存和磁盘空间
4. 查看控制台输出的错误信息
"""
    
    def _create_windows_scripts(self, package_dir, exe_name):
        """创建Windows批处理脚本"""
        # 启动脚本
        start_script = f"""@echo off
chcp 65001 > nul
echo PDF处理器启动中...
{exe_name} --gui
pause
"""
        (package_dir / 'start_gui.bat').write_text(start_script, encoding='utf-8')
        
        # 命令行脚本
        cmd_script = f"""@echo off
chcp 65001 > nul
echo 拖拽PDF文件到此窗口，然后按回车键处理
set /p input_file="请输入PDF文件路径: "
{exe_name} "%input_file%"
pause
"""
        (package_dir / 'process_pdf.bat').write_text(cmd_script, encoding='utf-8')
        print("✓ 创建Windows批处理脚本")
    
    def _create_linux_scripts(self, package_dir, exe_name):
        """创建Linux shell脚本"""
        # 启动脚本
        start_script = f"""#!/bin/bash
echo "PDF处理器启动中..."
./{exe_name} --gui
"""
        start_path = package_dir / 'start_gui.sh'
        start_path.write_text(start_script)
        start_path.chmod(0o755)
        
        # 命令行脚本
        cmd_script = f"""#!/bin/bash
echo "请输入PDF文件路径:"
read input_file
./{exe_name} "$input_file"
"""
        cmd_path = package_dir / 'process_pdf.sh'
        cmd_path.write_text(cmd_script)
        cmd_path.chmod(0o755)
        print("✓ 创建Linux shell脚本")
    
    def test_executable(self, package_dir):
        """测试可执行文件"""
        print("\n=== 测试可执行文件 ===")
        
        exe_name = 'pdf_processor'
        if self.platform == 'windows':
            exe_name += '.exe'
        
        exe_path = package_dir / exe_name
        
        # 测试帮助命令
        try:
            result = subprocess.run([str(exe_path), '--help'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✓ 可执行文件测试通过")
                return True
            else:
                print(f"✗ 可执行文件测试失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ 可执行文件测试异常: {e}")
            return False
    
    def build(self, clean=True, install_deps=True, debug=False, test=True):
        """完整构建流程
        
        Args:
            clean: 是否清理构建目录
            install_deps: 是否安装依赖
            debug: 是否启用调试模式
            test: 是否测试可执行文件
        """
        try:
            print("开始PDF处理器打包构建...")
            
            # 检查前提条件
            self.check_prerequisites()
            
            # 安装依赖
            if install_deps:
                self.install_dependencies()
            
            # 清理构建目录
            if clean:
                self.clean_build_dirs()
            
            # 构建可执行文件
            self.build_executable(debug=debug)
            
            # 创建分发包
            package_dir, archive_path = self.create_distribution_package()
            
            # 测试可执行文件
            if test:
                test_passed = self.test_executable(package_dir)
                if not test_passed:
                    print("警告: 可执行文件测试未通过，请手动验证")
            
            print(f"\n=== 构建完成 ===")
            print(f"分发包目录: {package_dir}")
            print(f"压缩包文件: {archive_path}")
            print(f"可执行文件大小: {(package_dir / ('pdf_processor.exe' if self.platform == 'windows' else 'pdf_processor')).stat().st_size / 1024 / 1024:.1f} MB")
            
            return True
            
        except Exception as e:
            print(f"\n构建失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PDF处理器自动化打包脚本')
    parser.add_argument('--no-clean', action='store_true', help='不清理构建目录')
    parser.add_argument('--no-deps', action='store_true', help='不安装依赖包')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--no-test', action='store_true', help='不测试可执行文件')
    parser.add_argument('--project-dir', help='项目目录路径')
    
    args = parser.parse_args()
    
    # 创建构建器
    builder = PDFProcessorBuilder(args.project_dir)
    
    # 执行构建
    success = builder.build(
        clean=not args.no_clean,
        install_deps=not args.no_deps,
        debug=args.debug,
        test=not args.no_test
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()