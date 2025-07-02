#!/usr/bin/env python3
"""
字幕烧录工具
将VTT字幕文件烧录到视频中
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_ffmpeg():
    """检查ffmpeg是否已安装"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def burn_subtitles(video_path, subtitle_path, output_path=None, font_size=24, font_color='white'):
    """
    将字幕烧录到视频中
    
    Args:
        video_path: 输入视频文件路径
        subtitle_path: 字幕文件路径（VTT格式）
        output_path: 输出视频文件路径（可选）
        font_size: 字体大小（默认24）
        font_color: 字体颜色（默认白色）
    """
    
    # 检查输入文件是否存在
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")
    
    if not os.path.exists(subtitle_path):
        raise FileNotFoundError(f"字幕文件不存在: {subtitle_path}")
    
    # 生成输出文件名
    if output_path is None:
        video_stem = Path(video_path).stem
        video_suffix = Path(video_path).suffix
        output_path = f"{video_stem}_with_subtitles{video_suffix}"
    
    # 构建ffmpeg命令
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"subtitles='{subtitle_path}':force_style='FontSize={font_size},PrimaryColour=&H{get_color_hex(font_color)}&'",
        '-c:a', 'copy',  # 音频不重新编码
        '-y',  # 覆盖输出文件
        output_path
    ]
    
    print(f"开始烧录字幕...")
    print(f"输入视频: {video_path}")
    print(f"字幕文件: {subtitle_path}")
    print(f"输出视频: {output_path}")
    print(f"字体设置: 大小={font_size}, 颜色={font_color}")
    print()
    
    try:
        # 执行ffmpeg命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 字幕烧录成功！")
            print(f"输出文件: {output_path}")
            
            # 显示文件大小信息
            original_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            print(f"原始文件大小: {original_size:.1f} MB")
            print(f"输出文件大小: {output_size:.1f} MB")
            
        else:
            print(f"❌ 字幕烧录失败！")
            print(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {e}")
        return False
    
    return True


def get_color_hex(color_name):
    """将颜色名称转换为十六进制值（BGR格式，用于ffmpeg）"""
    color_map = {
        'white': 'FFFFFF',
        'black': '000000',
        'red': '0000FF',
        'green': '00FF00',
        'blue': 'FF0000',
        'yellow': '00FFFF',
        'cyan': 'FFFF00',
        'magenta': 'FF00FF'
    }
    return color_map.get(color_name.lower(), 'FFFFFF')


def main():
    parser = argparse.ArgumentParser(
        description='将VTT字幕文件烧录到视频中',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python subtitle_burner.py video.mp4 subtitles.vtt
  python subtitle_burner.py video.mp4 subtitles.vtt -o output.mp4
  python subtitle_burner.py video.mp4 subtitles.vtt --font-size 28 --font-color yellow

支持的字体颜色:
  white, black, red, green, blue, yellow, cyan, magenta
        """
    )
    
    parser.add_argument('video', help='输入视频文件路径')
    parser.add_argument('subtitle', help='字幕文件路径（VTT格式）')
    parser.add_argument('-o', '--output', help='输出视频文件路径（默认自动生成）')
    parser.add_argument('--font-size', type=int, default=24, help='字体大小（默认24）')
    parser.add_argument('--font-color', default='white', 
                       choices=['white', 'black', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta'],
                       help='字体颜色（默认白色）')
    
    args = parser.parse_args()
    
    # 检查ffmpeg
    if not check_ffmpeg():
        print("❌ 错误: 未找到ffmpeg")
        print("请先安装ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  Windows: 从 https://ffmpeg.org/download.html 下载")
        sys.exit(1)
    
    # 执行字幕烧录
    success = burn_subtitles(
        video_path=args.video,
        subtitle_path=args.subtitle,
        output_path=args.output,
        font_size=args.font_size,
        font_color=args.font_color
    )
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()