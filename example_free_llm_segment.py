#!/usr/bin/env python3
"""
免费LLM视频分段工具使用示例
演示如何使用不同的免费LLM提供商进行智能视频分段
"""

import os
import subprocess
import sys

def check_files():
    """检查当前目录下的视频和字幕文件"""
    video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    vtt_files = [f for f in os.listdir('.') if f.endswith('.vtt')]
    
    print("🔍 检查当前目录下的文件...")
    print(f"视频文件: {video_files}")
    print(f"VTT字幕文件: {vtt_files}")
    
    if not video_files or not vtt_files:
        print("❌ 未找到视频文件或VTT字幕文件")
        return None, None
    
    return video_files[0], vtt_files[0]

def check_ffmpeg():
    """检查ffmpeg是否安装"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg已安装")
            return True
        else:
            print("❌ ffmpeg未正确安装")
            return False
    except FileNotFoundError:
        print("❌ 未找到ffmpeg，请先安装: brew install ffmpeg")
        return False

def check_ollama():
    """检查Ollama是否可用"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama可用，已安装模型: {[m['name'] for m in models]}")
            return True
        else:
            print("❌ Ollama服务未运行")
            return False
    except Exception as e:
        print(f"❌ Ollama不可用: {e}")
        return False

def example_rule_based():
    """示例1: 基于规则的分段（默认方法）"""
    print("\n" + "="*50)
    print("📋 示例1: 基于规则的智能分段")
    print("="*50)
    
    video, vtt = check_files()
    if not video or not vtt:
        return
    
    cmd = [
        'uv', 'run', 'free_llm_segmenter.py',
        video, vtt,
        '--provider', 'rule',
        '--duration', '35',
        '--dry-run'  # 仅分析，不实际分割
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd)

def example_ollama():
    """示例2: 使用Ollama本地模型分段"""
    print("\n" + "="*50)
    print("🤖 示例2: 使用Ollama本地模型智能分段")
    print("="*50)
    
    video, vtt = check_files()
    if not video or not vtt:
        return
    
    if not check_ollama():
        print("请先安装并启动Ollama:")
        print("1. 安装: brew install ollama")
        print("2. 启动服务: ollama serve")
        print("3. 下载模型: ollama pull llama3.2")
        return
    
    cmd = [
        'uv', 'run', 'free_llm_segmenter.py',
        video, vtt,
        '--provider', 'ollama',
        '--model', 'llama3.2',
        '--duration', '35',
        '--dry-run'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd)

def example_huggingface():
    """示例3: 使用Hugging Face免费API分段"""
    print("\n" + "="*50)
    print("🤗 示例3: 使用Hugging Face免费API智能分段")
    print("="*50)
    
    video, vtt = check_files()
    if not video or not vtt:
        return
    
    # 检查是否有API密钥
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    if not api_key:
        print("请设置Hugging Face API密钥:")
        print("export HUGGINGFACE_API_KEY='your_api_key_here'")
        print("或者在命令中使用 --api-key 参数")
        return
    
    cmd = [
        'uv', 'run', 'free_llm_segmenter.py',
        video, vtt,
        '--provider', 'huggingface',
        '--api-key', api_key,
        '--model', 'microsoft/DialoGPT-medium',
        '--duration', '35',
        '--dry-run'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd)

def example_actual_segment():
    """示例4: 实际分割视频（不使用dry-run）"""
    print("\n" + "="*50)
    print("✂️ 示例4: 实际分割视频")
    print("="*50)
    
    video, vtt = check_files()
    if not video or not vtt:
        return
    
    if not check_ffmpeg():
        return
    
    print("⚠️ 这将实际分割视频文件，确认继续？(y/N)")
    confirm = input().strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    cmd = [
        'uv', 'run', 'free_llm_segmenter.py',
        video, vtt,
        '--provider', 'rule',
        '--duration', '35',
        '--output', 'free_llm_segments'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd)

def example_custom_settings():
    """示例5: 自定义设置"""
    print("\n" + "="*50)
    print("⚙️ 示例5: 自定义设置")
    print("="*50)
    
    video, vtt = check_files()
    if not video or not vtt:
        return
    
    cmd = [
        'uv', 'run', 'free_llm_segmenter.py',
        video, vtt,
        '--provider', 'rule',
        '--duration', '40',  # 40秒片段
        '--output', 'custom_segments',
        '--dry-run'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd)

def show_help():
    """显示帮助信息"""
    print("\n" + "="*50)
    print("📖 免费LLM视频分段工具帮助")
    print("="*50)
    
    cmd = ['uv', 'run', 'free_llm_segmenter.py', '--help']
    subprocess.run(cmd)

def main():
    print("🎬 免费LLM视频分段工具使用示例")
    print("支持多种免费LLM提供商进行智能视频分段")
    
    while True:
        print("\n" + "="*50)
        print("请选择示例:")
        print("1. 基于规则的智能分段（推荐）")
        print("2. 使用Ollama本地模型分段")
        print("3. 使用Hugging Face免费API分段")
        print("4. 实际分割视频")
        print("5. 自定义设置")
        print("6. 显示帮助信息")
        print("0. 退出")
        print("="*50)
        
        choice = input("请输入选择 (0-6): ").strip()
        
        if choice == '1':
            example_rule_based()
        elif choice == '2':
            example_ollama()
        elif choice == '3':
            example_huggingface()
        elif choice == '4':
            example_actual_segment()
        elif choice == '5':
            example_custom_settings()
        elif choice == '6':
            show_help()
        elif choice == '0':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == '__main__':
    main()