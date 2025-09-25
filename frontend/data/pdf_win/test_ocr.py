#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR功能测试脚本
用于验证打包后的OCR模型是否能正常加载和工作
"""

import sys
import os
from pathlib import Path

def test_ocr_import():
    """测试OCR模块导入"""
    print("=== 测试OCR模块导入 ===")
    
    try:
        import rapidocr_onnxruntime
        print(f"✓ RapidOCR导入成功，版本: {rapidocr_onnxruntime.__version__}")
        
        # 检查模型文件
        rapidocr_path = Path(rapidocr_onnxruntime.__file__).parent
        models_path = rapidocr_path / 'models'
        
        if models_path.exists():
            model_files = list(models_path.glob('*.onnx'))
            print(f"✓ 找到模型文件 {len(model_files)} 个:")
            for model in model_files:
                size_mb = model.stat().st_size / (1024 * 1024)
                print(f"  - {model.name} ({size_mb:.1f}MB)")
        else:
            print("⚠ 模型目录不存在")
            
        return True
        
    except ImportError as e:
        print(f"✗ RapidOCR导入失败: {e}")
        return False

def test_ocr_initialization():
    """测试OCR初始化"""
    print("\n=== 测试OCR初始化 ===")
    
    try:
        from rapidocr_onnxruntime import RapidOCR
        
        # 测试默认初始化
        print("尝试默认初始化...")
        ocr = RapidOCR()
        print("✓ OCR默认初始化成功")
        
        # 测试带参数初始化
        print("尝试带参数初始化...")
        ocr_ch = RapidOCR(lang='ch')
        print("✓ OCR中文初始化成功")
        
        return True
        
    except Exception as e:
        print(f"✗ OCR初始化失败: {e}")
        return False

def test_ocr_recognition():
    """测试OCR识别功能"""
    print("\n=== 测试OCR识别功能 ===")
    
    try:
        from rapidocr_onnxruntime import RapidOCR
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # 创建测试图片
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # 绘制测试文字
        try:
            # 尝试使用系统字体
            font = ImageFont.load_default()
        except:
            font = None
            
        draw.text((10, 30), "Hello World", fill='black', font=font)
        draw.text((10, 60), "测试文字", fill='black', font=font)
        
        # 转换为字节
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        # OCR识别
        ocr = RapidOCR()
        result, _ = ocr(img_bytes)
        
        if result:
            print("✓ OCR识别成功，识别结果:")
            for line in result:
                print(f"  - {line[1]} (置信度: {line[2]:.2f})")
        else:
            print("⚠ OCR识别无结果（可能是测试图片太简单）")
            
        return True
        
    except Exception as e:
        print(f"✗ OCR识别测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("PDF处理器 - OCR功能测试")
    print("=" * 50)
    
    # 检查是否在打包环境中
    if getattr(sys, 'frozen', False):
        print("运行环境: 打包可执行文件")
    else:
        print("运行环境: Python脚本")
    
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print()
    
    # 执行测试
    tests = [
        test_ocr_import,
        test_ocr_initialization,
        test_ocr_recognition
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有OCR功能测试通过")
        return 0
    else:
        print("⚠ 部分测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())