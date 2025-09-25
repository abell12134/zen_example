# -*- mode: python ; coding: utf-8 -*-
"""
PDF处理器 PyInstaller 配置文件 - Windows版本
优化版本，解决OCR模型加载问题，专门针对Windows平台
"""

import os
import sys
from pathlib import Path

# 获取当前spec文件所在目录
SPECPATH = os.path.dirname(os.path.abspath(SPEC))

# 初始化数据文件列表
datas = []

# 收集RapidOCR模型文件和配置文件
try:
    import rapidocr_onnxruntime
    rapidocr_path = Path(rapidocr_onnxruntime.__file__).parent
    
    # 添加模型文件
    models_path = rapidocr_path / 'models'
    if models_path.exists():
        for model_file in models_path.glob('*.onnx'):
            datas.append((str(model_file), 'rapidocr_onnxruntime/models'))
        print(f"已添加RapidOCR模型文件: {len(list(models_path.glob('*.onnx')))} 个")
    
    # 添加配置文件
    config_path = rapidocr_path / 'config'
    if config_path.exists():
        for config_file in config_path.rglob('*'):
            if config_file.is_file():
                rel_path = config_file.relative_to(rapidocr_path)
                datas.append((str(config_file), f'rapidocr_onnxruntime/{rel_path.parent}'))
        print(f"已添加RapidOCR配置文件")
    
    # 添加其他必要文件
    for pattern in ['*.yaml', '*.yml', '*.json', '*.txt']:
        for config_file in rapidocr_path.glob(pattern):
            datas.append((str(config_file), 'rapidocr_onnxruntime'))
    
except ImportError as e:
    print(f"警告: 无法导入rapidocr_onnxruntime: {e}")

# 收集OpenCV数据文件
try:
    import cv2
    cv2_path = Path(cv2.__file__).parent
    cv2_data_path = cv2_path / 'data'
    if cv2_data_path.exists():
        for data_file in cv2_data_path.rglob('*'):
            if data_file.is_file():
                rel_path = data_file.relative_to(cv2_path)
                datas.append((str(data_file), f'cv2/{rel_path.parent}'))
        print(f"已添加OpenCV数据文件")
except ImportError as e:
    print(f"警告: 无法导入cv2: {e}")

# Windows特定的DLL文件收集
try:
    import onnxruntime
    onnx_path = Path(onnxruntime.__file__).parent
    # 收集ONNX Runtime的DLL文件
    for dll_file in onnx_path.glob('*.dll'):
        datas.append((str(dll_file), '.'))
    print(f"已添加ONNX Runtime DLL文件")
except ImportError:
    pass

# 隐藏导入模块列表
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'fitz',
    'openpyxl',
    'openpyxl.drawing.image',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'rapidocr_onnxruntime',
    'numpy',
    'cv2',
    'pyclipper',
    'jaraco.text',
    'pkg_resources',
    'setuptools',
    'onnxruntime',
    'shapely',
    'Polygon',
    'six',
    'yaml',
    'pyyaml',
    'pathlib',
    'threading',
    'queue',
    'io',
    'base64',
    'json',
    'datetime',
    'argparse',
    'shutil',
    'zipfile',
    'tempfile'
]

# 排除的模块列表
excludes = [
    'matplotlib',
    'scipy',
    'pandas',
    'jupyter',
    'IPython',
    'notebook',
    'pytest',
    'unittest',
    'test',
    'tkinter.test',
    'lib2to3',
    'pydoc_data'
]

# Windows特定的二进制文件
binaries = []

a = Analysis(
    ['pdf_processor_complete.py'],
    pathex=[SPECPATH],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pdf_processor',
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
    icon=None,  # 可以添加图标文件路径
)