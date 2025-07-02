#!/usr/bin/env python3
"""
视频分段工具使用示例
演示如何使用video_segmenter.py对视频进行智能分段
"""

import os
import subprocess
from pathlib import Path

def main():
    """演示视频分段功能"""
    
    # 当前目录
    current_dir = Path.cwd()
    
    # 查找视频和字幕文件
    video_file = None
    vtt_file = None
    
    for file in current_dir.glob("*.mp4"):
        if "cooking" in file.name.lower() or "english" in file.name.lower():
            video_file = file
            break
    
    for file in current_dir.glob("*.vtt"):
        if "cooking" in file.name.lower() or "english" in file.name.lower():
            vtt_file = file
            break
    
    if not video_file:
        print("❌ 未找到视频文件")
        print("请确保当前目录下有视频文件（.mp4）")
        return
    
    if not vtt_file:
        print("❌ 未找到VTT字幕文件")
        print("请确保当前目录下有VTT字幕文件（.vtt）")
        return
    
    print(f"📹 找到视频文件: {video_file.name}")
    print(f"📝 找到字幕文件: {vtt_file.name}")
    
    # 检查ffmpeg是否安装
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg 已安装")
        else:
            print("❌ ffmpeg 未正确安装")
            return
    except FileNotFoundError:
        print("❌ 未找到 ffmpeg")
        print("请先安装 ffmpeg: brew install ffmpeg")
        return
    
    print("\n🎬 视频分段工具使用示例:\n")
    
    # 示例1: 基本用法（不使用LLM）
    print("1️⃣ 基本用法（基于规则的分段）:")
    cmd1 = f"uv run video_segmenter.py '{video_file}' '{vtt_file}'"
    print(f"   {cmd1}")
    print("   - 使用基于规则的分段算法")
    print("   - 每段约35秒")
    print("   - 输出到 segments/ 目录\n")
    
    # 示例2: 自定义参数
    print("2️⃣ 自定义参数:")
    cmd2 = f"uv run video_segmenter.py '{video_file}' '{vtt_file}' -d 40 -o my_segments"
    print(f"   {cmd2}")
    print("   - 每段约40秒")
    print("   - 输出到 my_segments/ 目录\n")
    
    # 示例3: 仅分析模式
    print("3️⃣ 仅分析分段点（不生成视频）:")
    cmd3 = f"uv run video_segmenter.py '{video_file}' '{vtt_file}' --dry-run"
    print(f"   {cmd3}")
    print("   - 只分析和显示分段点")
    print("   - 不实际分割视频\n")
    
    # 示例4: 使用LLM（需要API密钥）
    print("4️⃣ 使用LLM智能分段（可选）:")
    cmd4 = f"uv run video_segmenter.py '{video_file}' '{vtt_file}' --api-key YOUR_API_KEY"
    print(f"   {cmd4}")
    print("   - 使用GPT等LLM进行智能分析")
    print("   - 需要OpenAI API密钥")
    print("   - 分段更加智能和自然\n")
    
    # 示例5: 使用免费的LLM替代方案
    print("5️⃣ 免费LLM替代方案:")
    print("   可以修改代码使用以下免费API:")
    print("   - Hugging Face Inference API")
    print("   - Google Colab + 本地模型")
    print("   - Ollama 本地运行")
    print("   - 通义千问、文心一言等国产模型\n")
    
    # 询问是否执行
    print("💡 提示:")
    print("   - 首次运行建议使用 --dry-run 查看分段效果")
    print("   - 分段后的视频文件会保存在指定目录")
    print("   - 每个片段都是独立的MP4文件")
    print("   - 可以根据需要调整 -d 参数改变片段长度\n")
    
    response = input("是否现在执行基本分段（仅分析模式）？(y/N): ")
    if response.lower() in ['y', 'yes', '是']:
        print("\n🚀 执行分段分析...")
        cmd = ['uv', 'run', 'video_segmenter.py', str(video_file), str(vtt_file), '--dry-run']
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ 执行失败: {e}")
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断")
    else:
        print("\n📚 你可以稍后手动运行上述命令")

if __name__ == '__main__':
    main()