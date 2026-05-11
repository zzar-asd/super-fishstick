# 正弦波生成器 (Sine Wave Generator)

本项目使用 Python 生成正弦波图像。

## 功能说明

运行 `sine_wave.py` 脚本将生成一个正弦波图像，并保存为 `sine_wave.png` 文件。

## 依赖项

- numpy
- matplotlib

安装依赖：
```bash
pip install numpy matplotlib
```

## 使用方法

```bash
python sine_wave.py
```

执行后将在当前目录生成 `sine_wave.png` 图像文件。

## 输出示例

生成的图像包含：
- 从 0 到 2π 的正弦曲线
- 坐标轴标签
- 网格线
- 图例

## 文件结构

```
/workspace/
├── sine_wave.py      # 主程序脚本
├── sine_wave.png     # 生成的正弦波图像
└── README.md         # 项目说明文档
```