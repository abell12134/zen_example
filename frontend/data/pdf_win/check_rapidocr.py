#!/usr/bin/env python3
import rapidocr_onnxruntime
from pathlib import Path

print('RapidOCR路径:', Path(rapidocr_onnxruntime.__file__).parent)
models_path = Path(rapidocr_onnxruntime.__file__).parent / 'models'
print('模型目录:', models_path)
print('模型文件存在:', models_path.exists())

if models_path.exists():
    print('模型文件列表:')
    for f in models_path.rglob('*'):
        if f.is_file():
            print('  -', f.name, f'({f.stat().st_size / 1024 / 1024:.1f}MB)')
else:
    print('模型目录不存在，检查其他可能的位置...')
    
    # 检查包的根目录
    rapidocr_root = Path(rapidocr_onnxruntime.__file__).parent
    print('包根目录内容:')
    for item in rapidocr_root.iterdir():
        print('  -', item.name, '(目录)' if item.is_dir() else '(文件)')
        
    # 检查是否有其他模型相关目录
    for pattern in ['*model*', '*onnx*', '*det*', '*rec*', '*cls*']:
        matches = list(rapidocr_root.rglob(pattern))
        if matches:
            print(f'找到匹配 {pattern} 的文件/目录:')
            for match in matches:
                print('  -', match.relative_to(rapidocr_root))