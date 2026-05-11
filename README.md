# super-fishstick

本项目包含多个 Python 脚本，用于生成图形图像和处理视频。

## 功能说明

### 1. 正弦波图像生成 (`generate_sine_wave.py`)

使用 `matplotlib` 和 `numpy` 库生成正弦波图像。

**运行方式：**
```bash
python3 generate_sine_wave.py
```

**输出：**
- `sine_wave.png` - 包含 0 到 4π 范围内的正弦波图像

**依赖：**
```bash
pip install numpy matplotlib
```

### 2. SVG 圆柱体生成 (`generate_cylinder_svg.py`)

使用纯 Python 生成 SVG 格式的圆柱体图像，带有渐变效果以呈现 3D 视觉。

**运行方式：**
```bash
python3 generate_cylinder_svg.py
```

**输出：**
- `cylinder.svg` - 可缩放矢量图形格式的圆柱体图像

**依赖：**
- 无需额外依赖，使用 Python 标准库即可

### 3. 视频过滤、水印去除和尺寸调整 (`video_filter_watermark.py`)

使用 `opencv-python` 和 `moviepy` 库进行视频滤镜应用、水印去除和尺寸调整。

**运行方式：**

应用视频滤镜：
```bash
# 模糊滤镜
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode filter --filter-type blur

# 锐化滤镜
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode filter --filter-type sharpen

# 灰度滤镜
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode filter --filter-type grayscale

# 棕褐色滤镜
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode filter --filter-type sepia

# 边缘检测
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode filter --filter-type edge
```

去除水印：
```bash
# 使用 OpenCV 方法（默认，自动检测右下角水印）
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode watermark

# 使用 MoviePy 方法
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode watermark --method moviepy

# 指定水印区域 (x, y, width, height)
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode watermark --watermark-area 100 100 50 50
```

调整视频尺寸/比例：
```bash
# 使用缩放因子（缩小到 50%）
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode resize --scale 0.5

# 放大到 2 倍
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode resize --scale 2.0

# 指定目标尺寸（宽 640 高 480）
python3 video_filter_watermark.py -i input.mp4 -o output.mp4 --mode resize --size 640 480
```

**参数说明：**
- `-i, --input`: 输入视频文件路径（必需）
- `-o, --output`: 输出视频文件路径（必需）
- `-m, --mode`: 操作模式，`filter`（滤镜）、`watermark`（去水印）或 `resize`（调整尺寸）
- `-f, --filter-type`: 滤镜类型（blur, sharpen, grayscale, sepia, edge, none）
- `--method`: 去水印方法（opencv 或 moviepy）
- `--watermark-area`: 水印区域坐标 (x, y, width, height)
- `-s, --scale`: 缩放因子（仅在 resize 模式下使用，例如 0.5 缩小一半，2.0 放大两倍）
- `--size`: 目标尺寸 (width height)（仅在 resize 模式下使用，优先级高于 scale）

**支持的滤镜类型：**
- `blur`: 高斯模糊
- `sharpen`: 锐化
- `grayscale`: 灰度化
- `sepia`: 棕褐色复古效果
- `edge`: 边缘检测
- `none`: 无滤镜

**依赖：**
```bash
pip install opencv-python moviepy numpy
```

## 文件结构

```
/workspace
├── README.md                    # 项目说明文档
├── generate_sine_wave.py        # 正弦波生成脚本
├── generate_cylinder_svg.py     # SVG 圆柱体生成脚本
├── video_filter_watermark.py    # 视频过滤和水印去除脚本
├── sine_wave.png                # 生成的正弦波图像
└── cylinder.svg                 # 生成的圆柱体 SVG 图像
```

## 使用方法

1. 克隆或下载本项目到本地
2. 安装所需依赖（仅正弦波脚本需要）：
   ```bash
   pip install numpy matplotlib
   ```
3. 运行相应的脚本生成图像
4. 查看生成的图像文件

## 示例图像

### 正弦波
![Sine Wave](sine_wave.png)

### 圆柱体
SVG 文件可在浏览器中直接打开查看：
```bash
# Linux/Mac
xdg-open cylinder.svg    # Linux
open cylinder.svg        # Mac

# Windows
start cylinder.svg
```