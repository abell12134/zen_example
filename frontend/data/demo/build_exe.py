#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF处理工具打包脚本
使用PyInstaller将pdf_processor_complete.py打包成Windows可执行程序
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_and_install_package(package_name, import_name=None, pip_name=None, optional=False):
    """检查并安装单个包
    
    Args:
        package_name: 显示名称
        import_name: 导入时使用的名称，默认与package_name相同
        pip_name: pip安装时使用的名称，默认与package_name相同
        optional: 是否为可选包，可选包安装失败不会导致整体失败
    
    Returns:
        bool: 安装成功返回True，失败返回False
    """
    if import_name is None:
        import_name = package_name
    if pip_name is None:
        pip_name = package_name
    
    try:
        # 特殊处理RapidOCR，因为它可能有DLL依赖问题
        if import_name == 'rapidocr_onnxruntime':
            try:
                from rapidocr_onnxruntime import RapidOCR
                # 尝试实例化以检查DLL是否正常
                ocr = RapidOCR()
                print(f"✓ {package_name} 已安装且可正常使用")
                return True
            except Exception as e:
                if "DLL load failed" in str(e) or "onnxruntime" in str(e):
                    print(f"⚠ {package_name} 已安装但存在DLL依赖问题: {e}")
                    print(f"  建议: 尝试重新安装 onnxruntime 或使用备用OCR引擎")
                    if optional:
                        return True  # 标记为可选，不阻止构建
                    return False
                else:
                    raise e
        else:
            __import__(import_name)
        
        print(f"✓ {package_name} 已安装")
        return True
    except ImportError:
        print(f"× {package_name} 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            print(f"✓ {package_name} 安装成功")
            
            # 对于RapidOCR，安装后再次检查DLL依赖
            if import_name == 'rapidocr_onnxruntime':
                try:
                    from rapidocr_onnxruntime import RapidOCR
                    ocr = RapidOCR()
                    print(f"✓ {package_name} DLL依赖检查通过")
                except Exception as e:
                    if "DLL load failed" in str(e):
                        print(f"⚠ {package_name} 安装成功但DLL依赖有问题")
                        print(f"  尝试安装Microsoft Visual C++ Redistributable")
                        print(f"  或使用: pip install onnxruntime --force-reinstall")
                        if optional:
                            return True
                        return False
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"× {package_name} 安装失败: {e}")
            return False

def check_system_dependencies():
    """检查系统依赖"""
    print("\n检查系统依赖...")
    
    # 检查Visual C++ Redistributable (Windows)
    if sys.platform.startswith('win'):
        print("检查Microsoft Visual C++ Redistributable...")
        try:
            import winreg
            # 检查常见的VC++ Redistributable注册表项
            vc_versions = [
                "Microsoft Visual C++ 2015-2022 Redistributable (x64)",
                "Microsoft Visual C++ 2019 Redistributable (x64)",
                "Microsoft Visual C++ 2017 Redistributable (x64)",
                "Microsoft Visual C++ 2015 Redistributable (x64)"
            ]
            
            found_vc = False
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        try:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            for vc_version in vc_versions:
                                if vc_version in display_name:
                                    print(f"✓ 找到: {display_name}")
                                    found_vc = True
                                    break
                        except FileNotFoundError:
                            pass
                        winreg.CloseKey(subkey)
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except Exception as e:
                print(f"检查注册表时出错: {e}")
            
            if not found_vc:
                print("⚠ 警告: 未找到Microsoft Visual C++ Redistributable")
                print("  这可能导致onnxruntime DLL加载失败")
                print("  建议下载安装: https://aka.ms/vs/17/release/vc_redist.x64.exe")
                return False
            else:
                print("✓ Microsoft Visual C++ Redistributable 已安装")
                
        except ImportError:
            print("⚠ 无法检查Visual C++ Redistributable (winreg模块不可用)")
    
    # 检查其他系统依赖
    print("检查其他系统库...")
    
    # 检查是否有必要的系统库
    try:
        import ctypes
        # 尝试加载一些常见的系统库
        if sys.platform.startswith('win'):
            try:
                ctypes.windll.kernel32
                print("✓ Windows系统库可用")
            except Exception as e:
                print(f"⚠ Windows系统库检查失败: {e}")
        elif sys.platform.startswith('linux'):
            try:
                ctypes.CDLL("libc.so.6")
                print("✓ Linux系统库可用")
            except Exception as e:
                print(f"⚠ Linux系统库检查失败: {e}")
    except Exception as e:
        print(f"系统库检查出错: {e}")
    
    return True

def check_required_packages():
    """检查并安装所有必需的包"""
    print("=" * 50)
    print("检查必需的Python包...")
    print("=" * 50)
    
    # 定义必需的包列表
    required_packages = [
        # (显示名称, 导入名称, pip安装名称, 是否可选)
        ("PyInstaller", "PyInstaller", "pyinstaller", False),
        ("PyMuPDF", "fitz", "PyMuPDF", False),
        ("OpenPyXL", "openpyxl", "openpyxl", False),
        ("Pillow", "PIL", "Pillow", False),
        ("NumPy", "numpy", "numpy", False),
    ]
    
    # OCR引擎（可选，但至少需要一个）
    ocr_packages = [
        ("RapidOCR", "rapidocr_onnxruntime", "rapidocr-onnxruntime", True),
        ("PaddleOCR", "paddleocr", "paddleocr", True),
    ]
    
    # 可选包（GUI相关，通常系统自带）
    optional_packages = [
        ("Tkinter", "tkinter", None, True),  # 通常系统自带，不需要pip安装
    ]
    
    failed_packages = []
    
    # 检查必需包
    for display_name, import_name, pip_name, is_optional in required_packages:
        if not check_and_install_package(display_name, import_name, pip_name, is_optional):
            failed_packages.append(display_name)
    
    # 检查OCR引擎
    print("\n检查OCR引擎...")
    ocr_available = False
    for display_name, import_name, pip_name, is_optional in ocr_packages:
        if check_and_install_package(display_name, import_name, pip_name, is_optional):
            ocr_available = True
            break  # 只要有一个OCR引擎可用就行
    
    if not ocr_available:
        print("⚠ 警告: 没有可用的OCR引擎，程序可能无法正常工作")
        print("  建议手动安装: pip install rapidocr-onnxruntime 或 pip install paddleocr")
        
        # 询问用户是否继续
        choice = input("\n是否继续构建？(y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            print("构建已取消")
            return False
    
    # 检查可选包
    print("\n检查可选包...")
    for display_name, import_name, pip_name, is_optional in optional_packages:
        try:
            __import__(import_name)
            print(f"✓ {display_name} 可用")
        except ImportError:
            if pip_name:
                print(f"× {display_name} 不可用，尝试安装...")
                check_and_install_package(display_name, import_name, pip_name, is_optional)
            else:
                print(f"⚠ {display_name} 不可用（通常系统自带，可能需要重新安装Python）")
    
    if failed_packages:
        print(f"\n❌ 以下关键包安装失败: {', '.join(failed_packages)}")
        print("请手动安装这些包后重试")
        return False
    
    print(f"\n✅ 包依赖检查完成")
    return True

def check_pyinstaller():
    """检查PyInstaller是否已安装（保持向后兼容）"""
    return check_and_install_package("PyInstaller", "PyInstaller", "pyinstaller")

def create_spec_file():
    """创建PyInstaller规格文件"""
    print("\n创建PyInstaller规格文件...")
    
    # 获取onnxruntime和rapidocr的路径
    import sys
    import os
    
    try:
        import onnxruntime
        onnxruntime_path = os.path.dirname(onnxruntime.__file__)
        onnxruntime_capi_path = os.path.join(onnxruntime_path, 'capi')
    except ImportError:
        onnxruntime_path = ""
        onnxruntime_capi_path = ""
    
    try:
        import rapidocr_onnxruntime
        rapidocr_path = os.path.dirname(rapidocr_onnxruntime.__file__)
        rapidocr_models_path = os.path.join(rapidocr_path, 'models')
    except ImportError:
        rapidocr_path = ""
        rapidocr_models_path = ""
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# 动态获取onnxruntime和rapidocr路径
onnxruntime_path = r"{onnxruntime_path}"
rapidocr_path = r"{rapidocr_path}"

# 收集onnxruntime的二进制文件
onnxruntime_binaries = []
if onnxruntime_path and os.path.exists(onnxruntime_path):
    capi_path = os.path.join(onnxruntime_path, 'capi')
    if os.path.exists(capi_path):
        for file in os.listdir(capi_path):
            if file.endswith(('.so', '.dll', '.dylib')):
                src = os.path.join(capi_path, file)
                dst = os.path.join('onnxruntime', 'capi')
                onnxruntime_binaries.append((src, dst))

# 收集rapidocr的模型文件
rapidocr_datas = []
if rapidocr_path and os.path.exists(rapidocr_path):
    models_path = os.path.join(rapidocr_path, 'models')
    if os.path.exists(models_path):
        rapidocr_datas.append((models_path, 'rapidocr_onnxruntime/models'))

a = Analysis(
    ['pdf_processor_complete.py'],
    pathex=[],
    binaries=onnxruntime_binaries + [
        # 手动添加关键的onnxruntime文件
    ],
    datas=[
        ('ocr', 'ocr'),
    ] + rapidocr_datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'rapidocr_onnxruntime',
        'rapidocr_onnxruntime.main',
        'rapidocr_onnxruntime.ch_ppocr_det',
        'rapidocr_onnxruntime.ch_ppocr_cls',
        'rapidocr_onnxruntime.ch_ppocr_rec',
        'rapidocr_onnxruntime.utils',
        'paddleocr',
        'openpyxl',
        'fitz',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'onnxruntime',
        'onnxruntime.capi',
        'onnxruntime.capi.onnxruntime_pybind11_state',
        'onnxruntime.backend',
        'numpy',
        'cv2',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDF处理工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('pdf_processor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ 规格文件已创建: pdf_processor.spec")
    print("✓ 已自动配置onnxruntime和rapidocr的依赖收集")
    print(f"✓ ONNX Runtime路径: {onnxruntime_capi_path}")
    print(f"✓ RapidOCR路径: {rapidocr_models_path}")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 清理之前的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("已清理build目录")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("已清理dist目录")
    
    try:
        # 使用规格文件构建
        cmd = [sys.executable, "-m", "PyInstaller", "pdf_processor.spec"]
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("\n构建成功！")
            print("可执行文件位置: dist/PDF处理工具.exe")
            
            # 检查文件是否存在
            exe_path = Path('dist/PDF处理工具.exe')
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"文件大小: {size_mb:.1f} MB")
            else:
                print("警告: 可执行文件未找到")
        else:
            print("\n构建失败！")
            print("错误输出:")
            print(result.stderr)
            
    except Exception as e:
        print(f"构建过程中发生错误: {e}")

def create_simple_build():
    """创建简单的一键构建命令"""
    print("\n使用简单命令构建...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 打包成单个文件
        "--console",  # 保留控制台窗口（而不是--windowed）
        "--name=PDF处理工具",
        "--add-data=ocr;ocr",  # 如果有OCR目录
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=rapidocr_onnxruntime",
        "--hidden-import=rapidocr_onnxruntime.main",
        "--hidden-import=rapidocr_onnxruntime.ch_ppocr_det",
        "--hidden-import=rapidocr_onnxruntime.ch_ppocr_cls", 
        "--hidden-import=rapidocr_onnxruntime.ch_ppocr_rec",
        "--hidden-import=rapidocr_onnxruntime.utils",
        "--hidden-import=paddleocr",
        "--hidden-import=openpyxl",
        "--hidden-import=fitz",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=onnxruntime",
        "--hidden-import=onnxruntime.capi",
        "--hidden-import=onnxruntime.capi.onnxruntime_pybind11_state",
        "--hidden-import=onnxruntime.backend",
        "--collect-all=onnxruntime",  # 收集所有onnxruntime相关文件
        "--collect-all=rapidocr_onnxruntime",  # 收集所有rapidocr相关文件
        "--collect-data=onnxruntime",  # 收集onnxruntime数据文件
        "--collect-data=rapidocr_onnxruntime",  # 收集rapidocr数据文件
        "pdf_processor_complete.py"
    ]
    
    try:
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("\n简单构建成功！")
            exe_path = Path('dist/PDF处理工具.exe')
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"可执行文件: {exe_path}")
                print(f"文件大小: {size_mb:.1f} MB")
        else:
            print("\n简单构建失败！")
            print("错误输出:")
            print(result.stderr)
            
    except Exception as e:
        print(f"简单构建过程中发生错误: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("PDF处理工具 - Windows可执行程序打包脚本")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('pdf_processor_complete.py'):
        print("错误: 未找到pdf_processor_complete.py文件")
        print("请确保在正确的目录下运行此脚本")
        return
    
    # 检查系统依赖
    if not check_system_dependencies():
        print("\n⚠ 系统依赖检查发现问题，但将继续构建...")
        response = input("是否继续构建？(y/n): ")
        if response.lower() != 'y':
            print("构建已取消")
            return
    
    # 检查并安装所有必需的包
    if not check_required_packages():
        print("\n❌ 包依赖检查失败，无法继续构建")
        return
    
    print("\n选择构建方式:")
    print("1. 使用规格文件构建（推荐，可自定义配置）")
    print("2. 使用简单命令构建（快速）")
    print("3. 两种方式都尝试")
    
    choice = input("\n请选择 (1/2/3，默认为1): ").strip() or "1"
    
    if choice == "1":
        create_spec_file()
        build_executable()
    elif choice == "2":
        create_simple_build()
    elif choice == "3":
        print("\n=== 方式1: 规格文件构建 ===")
        create_spec_file()
        build_executable()
        
        print("\n=== 方式2: 简单命令构建 ===")
        create_simple_build()
    else:
        print("无效选择，使用默认方式")
        create_spec_file()
        build_executable()
    
    print("\n=== 构建完成 ===")
    print("如果构建成功，可执行文件位于 dist/ 目录中")
    print("可以将整个dist目录复制到Windows系统中运行")

if __name__ == "__main__":
    main()