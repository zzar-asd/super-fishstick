#!/usr/bin/env python3
"""
视频过滤和水印去除脚本
支持多种视频滤镜效果和水印去除功能
"""

import cv2
import numpy as np
import argparse
from moviepy import VideoFileClip, vfx


def apply_filter(input_path, output_path, filter_type='none'):
    """
    应用视频滤镜
    
    参数:
        input_path: 输入视频路径
        output_path: 输出视频路径
        filter_type: 滤镜类型 (blur, sharpen, grayscale, sepia, edge, none)
    """
    cap = cv2.VideoCapture(input_path)
    
    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件: {input_path}")
    
    # 获取视频属性
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    filter_functions = {
        'blur': lambda frame: cv2.GaussianBlur(frame, (15, 15), 0),
        'sharpen': lambda frame: cv2.filter2D(frame, -1, np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ])),
        'grayscale': lambda frame: cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR),
        'sepia': lambda frame: apply_sepia(frame),
        'edge': lambda frame: cv2.Canny(frame, 100, 200),
        'none': lambda frame: frame
    }
    
    if filter_type not in filter_functions:
        raise ValueError(f"不支持的滤镜类型: {filter_type}")
    
    filter_func = filter_functions[filter_type]
    frame_count = 0
    
    print(f"正在应用 {filter_type} 滤镜...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 对于边缘检测，需要转换为三通道
        if filter_type == 'edge':
            filtered = cv2.cvtColor(filter_func(frame), cv2.COLOR_GRAY2BGR)
        else:
            filtered = filter_func(frame)
        
        out.write(filtered)
        frame_count += 1
        
        if frame_count % 100 == 0:
            print(f"已处理 {frame_count} 帧")
    
    cap.release()
    out.release()
    print(f"滤镜应用完成！共处理 {frame_count} 帧，输出到: {output_path}")


def apply_sepia(frame):
    """应用棕褐色滤镜"""
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia = cv2.transform(frame, kernel)
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    return sepia


def remove_watermark_moviepy(input_path, output_path, watermark_area=None):
    """
    使用 MoviePy 进行简单的水印去除（裁剪或模糊）
    
    参数:
        input_path: 输入视频路径
        output_path: 输出视频路径
        watermark_area: 水印区域 (x, y, width, height)，如果为 None 则自动检测右下角
    """
    clip = VideoFileClip(input_path)
    
    if watermark_area is None:
        # 默认去除右下角水印
        w, h = clip.size
        watermark_area = (int(w * 0.8), int(h * 0.8), int(w * 0.2), int(h * 0.2))
    
    x, y, w, h = watermark_area
    
    def blur_watermark(get_frame, t):
        frame = get_frame(t)
        frame_copy = frame.copy()
        
        # 确保坐标在有效范围内
        x_end = min(x + w, frame.shape[1])
        y_end = min(y + h, frame.shape[0])
        x_start = max(0, x)
        y_start = max(0, y)
        
        if x_start < x_end and y_start < y_end:
            # 对水印区域应用高斯模糊
            roi = frame_copy[y_start:y_end, x_start:x_end]
            blurred_roi = cv2.GaussianBlur(roi, (21, 21), 0)
            frame_copy[y_start:y_end, x_start:x_end] = blurred_roi
        
        return frame_copy
    
    # 应用水印模糊效果
    processed_clip = clip.fl(blur_watermark)
    
    print("正在去除水印...")
    processed_clip.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    
    clip.close()
    processed_clip.close()
    print(f"水印去除完成！输出到: {output_path}")


def remove_watermark_opencv(input_path, output_path, watermark_area=None):
    """
    使用 OpenCV 进行水印去除（修复/补全）
    
    参数:
        input_path: 输入视频路径
        output_path: 输出视频路径
        watermark_area: 水印区域 (x, y, width, height)
    """
    cap = cv2.VideoCapture(input_path)
    
    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件: {input_path}")
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if watermark_area is None:
        # 默认去除右下角水印
        watermark_area = (int(width * 0.8), int(height * 0.8), int(width * 0.2), int(height * 0.2))
    
    x, y, w, h = watermark_area
    frame_count = 0
    
    print("正在使用 OpenCV 去除水印...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 创建掩码
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        # 确保坐标在有效范围内
        x_end = min(x + w, frame.shape[1])
        y_end = min(y + h, frame.shape[0])
        x_start = max(0, x)
        y_start = max(0, y)
        
        if x_start < x_end and y_start < y_end:
            # 在掩码上标记水印区域
            mask[y_start:y_end, x_start:x_end] = 255
            
            # 使用 inpainting 修复水印区域
            frame = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
        
        out.write(frame)
        frame_count += 1
        
        if frame_count % 100 == 0:
            print(f"已处理 {frame_count} 帧")
    
    cap.release()
    out.release()
    print(f"水印去除完成！共处理 {frame_count} 帧，输出到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='视频过滤和水印去除工具')
    parser.add_argument('--input', '-i', required=True, help='输入视频文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出视频文件路径')
    parser.add_argument('--mode', '-m', choices=['filter', 'watermark'], default='filter',
                       help='操作模式：filter(滤镜) 或 watermark(去水印)')
    parser.add_argument('--filter-type', '-f', 
                       choices=['blur', 'sharpen', 'grayscale', 'sepia', 'edge', 'none'],
                       default='none', help='滤镜类型（仅在 filter 模式下使用）')
    parser.add_argument('--method', choices=['opencv', 'moviepy'], default='opencv',
                       help='去水印方法（仅在 watermark 模式下使用）')
    parser.add_argument('--watermark-area', type=int, nargs=4, metavar=('X', 'Y', 'W', 'H'),
                       help='水印区域坐标 (x, y, width, height)')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'filter':
            apply_filter(args.input, args.output, args.filter_type)
        elif args.mode == 'watermark':
            if args.method == 'opencv':
                remove_watermark_opencv(args.input, args.output, args.watermark_area)
            else:
                remove_watermark_moviepy(args.input, args.output, args.watermark_area)
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
