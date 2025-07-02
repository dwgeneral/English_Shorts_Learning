#!/usr/bin/env python3
"""
字幕烧录使用示例
演示如何使用subtitle_burner.py将VTT字幕烧录到视频中
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """演示字幕烧录功能"""
    
    print("🔥 字幕烧录功能演示")
    print("=" * 50)
    
    # 检查当前目录中的文件
    current_dir = Path(".")
    video_files = list(current_dir.glob("*.mp4"))
    vtt_files = list(current_dir.glob("*.vtt"))
    
    print(f"📁 当前目录: {current_dir.absolute()}")
    print(f"🎥 找到的视频文件: {len(video_files)}")
    for video in video_files:
        print(f"   - {video.name}")
    
    print(f"📝 找到的字幕文件: {len(vtt_files)}")
    for vtt in vtt_files:
        print(f"   - {vtt.name}")
    
    if not video_files:
        print("\n❌ 未找到MP4视频文件")
        print("请确保当前目录中有视频文件，或使用以下命令下载：")
        print('uv run youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"')
        return
    
    if not vtt_files:
        print("\n❌ 未找到VTT字幕文件")
        print("请确保当前目录中有字幕文件，或在下载视频时会自动下载字幕")
        return
    
    # 选择第一个视频和字幕文件进行演示
    video_file = video_files[0]
    vtt_file = vtt_files[0]
    
    print(f"\n🎯 将使用以下文件进行演示:")
    print(f"   视频: {video_file.name}")
    print(f"   字幕: {vtt_file.name}")
    
    # 检查ffmpeg是否安装
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("\n✅ ffmpeg 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n❌ 未找到ffmpeg，请先安装:")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   Windows: 从 https://ffmpeg.org/download.html 下载")
        return
    
    # 演示不同的烧录选项
    examples = [
        {
            "name": "基本烧录（白色字幕，24号字体）",
            "cmd": ["uv", "run", "subtitle_burner.py", str(video_file), str(vtt_file)]
        },
        {
            "name": "黄色字幕，28号字体",
            "cmd": ["uv", "run", "subtitle_burner.py", str(video_file), str(vtt_file), 
                   "--font-size", "28", "--font-color", "yellow", 
                   "-o", f"{video_file.stem}_yellow_subs.mp4"]
        },
        {
            "name": "红色字幕，32号字体",
            "cmd": ["uv", "run", "subtitle_burner.py", str(video_file), str(vtt_file), 
                   "--font-size", "32", "--font-color", "red", 
                   "-o", f"{video_file.stem}_red_subs.mp4"]
        }
    ]
    
    print("\n📋 可用的烧录选项:")
    for i, example in enumerate(examples, 1):
        print(f"   {i}. {example['name']}")
    
    try:
        choice = input("\n请选择要执行的选项 (1-3, 或按Enter跳过): ").strip()
        
        if not choice:
            print("\n⏭️ 跳过演示")
            return
        
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(examples):
            selected = examples[choice_idx]
            print(f"\n🚀 执行: {selected['name']}")
            print(f"命令: {' '.join(selected['cmd'])}")
            print("\n⏳ 开始烧录...")
            
            result = subprocess.run(selected['cmd'])
            
            if result.returncode == 0:
                print("\n✅ 烧录完成！")
            else:
                print("\n❌ 烧录失败")
        else:
            print("\n❌ 无效选择")
            
    except ValueError:
        print("\n❌ 请输入有效数字")
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()