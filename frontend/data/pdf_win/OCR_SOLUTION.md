# PDF处理器 - OCR模型加载问题解决方案

## 问题描述

在使用PyInstaller打包PDF处理器时，程序启动时出现OCR模型加载失败的问题。主要表现为：
- RapidOCR模型文件无法找到
- 程序无法正常初始化OCR功能
- 打包后的可执行文件缺少必要的模型文件

## 解决方案

### 1. 优化的PyInstaller配置文件 (pdf_processor.spec)

创建了专门的spec文件来正确处理OCR模型文件的打包：

```python
# 收集RapidOCR模型文件和配置文件
try:
    import rapidocr_onnxruntime
    rapidocr_path = Path(rapidocr_onnxruntime.__file__).parent
    
    # 添加模型文件
    models_path = rapidocr_path / 'models'
    if models_path.exists():
        for model_file in models_path.glob('*.onnx'):
            datas.append((str(model_file), 'rapidocr_onnxruntime/models'))
    
    # 添加配置文件
    config_path = rapidocr_path / 'config'
    if config_path.exists():
        for config_file in config_path.rglob('*'):
            if config_file.is_file():
                rel_path = config_file.relative_to(rapidocr_path)
                datas.append((str(config_file), f'rapidocr_onnxruntime/{rel_path.parent}'))
```

### 2. 代码中的OCR初始化优化

在`pdf_processor_complete.py`中实现了智能的OCR初始化策略：

```python
class RapidOCRWrapper(BaseOCR):
    def __init__(self, lang: str = "ch"):
        try:
            # 在打包环境中，尝试不使用配置文件初始化
            if getattr(sys, 'frozen', False):
                # 打包环境，使用最简单的初始化方式
                self.ocr = RapidOCR()
            else:
                # 正常环境
                self.ocr = RapidOCR(lang=lang)
        except Exception as e:
            # 尝试使用默认配置初始化
            self.ocr = RapidOCR()
```

### 3. 模型文件包含情况

通过检查脚本确认，RapidOCR包含以下模型文件：
- `ch_ppocr_mobile_v2.0_cls_infer.onnx` (0.6MB) - 文字方向分类器
- `ch_PP-OCRv4_det_infer.onnx` (4.5MB) - 文字检测模型
- `ch_PP-OCRv4_rec_infer.onnx` (10.4MB) - 文字识别模型

### 4. 隐藏导入模块优化

在spec文件中添加了必要的隐藏导入：

```python
hiddenimports = [
    'tkinter',
    'fitz',
    'openpyxl',
    'PIL',
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
    'pyyaml'
]
```

## 测试结果

### 构建测试
- ✅ 构建成功，无错误
- ✅ 模型文件正确包含（3个ONNX文件）
- ✅ 可执行文件大小：154.8 MB
- ✅ 基本功能测试通过

### OCR功能测试
- ✅ OCR模块导入成功
- ✅ OCR初始化成功（默认和中文模式）
- ✅ OCR识别功能正常工作
- ⚠️ 版本信息获取失败（不影响核心功能）

## 使用方法

### 1. 构建可执行文件
```bash
cd /root/project/zen_example/frontend/data/pdf_win
python build.py --no-deps
```

### 2. 测试OCR功能
```bash
# 在打包目录中
python test_ocr.py
```

### 3. 运行程序
```bash
# 查看帮助
./pdf_processor --help

# GUI模式
./pdf_processor --gui

# 处理PDF文件
./pdf_processor -p input.pdf
```

## 关键改进点

1. **模型文件正确打包**：通过spec文件确保所有ONNX模型文件都被包含在可执行文件中
2. **智能初始化策略**：根据运行环境（打包vs开发）选择不同的初始化方式
3. **依赖管理优化**：添加必要的隐藏导入，移除冲突的排除项
4. **错误处理增强**：提供多层次的初始化回退机制

## 注意事项

1. **首次运行**：可能需要较长的初始化时间
2. **磁盘空间**：确保有足够空间用于临时文件
3. **权限问题**：确保程序有足够的文件读写权限
4. **网络连接**：某些情况下可能需要网络连接

## 环境要求

### 构建环境
- Python 3.8+
- PyInstaller 6.0+
- rapidocr-onnxruntime 1.3.0+
- 其他依赖见 requirements_packaging.txt

### 运行环境
- 目标机器无需安装Python
- Linux x86_64 系统
- 至少200MB可用磁盘空间
- 基本的系统库支持

## 故障排除

如果仍然遇到OCR加载问题：

1. 检查可执行文件是否包含模型文件
2. 确认运行环境有足够权限
3. 查看程序输出的详细错误信息
4. 尝试在终端中运行以获取完整日志

通过以上解决方案，PDF处理器的OCR功能在打包后能够正常工作，解决了模型加载失败的问题。