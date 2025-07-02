#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube视频下载器
使用yt-dlp库下载YouTube视频到当前目录

使用方法:
python youtube_downloader.py
然后输入YouTube视频链接

或者:
python youtube_downloader.py <YouTube_URL>
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import glob

def convert_vtt_to_text_auto(output_path):
    """自动检测并转换VTT文件为纯文本格式"""
    try:
        # 导入VTT转换模块
        from vtt_to_text_converter import convert_vtt_to_text
        
        # 查找VTT文件
        vtt_pattern = os.path.join(output_path, '*.vtt')
        vtt_files = glob.glob(vtt_pattern)
        
        if not vtt_files:
            print("📝 未找到VTT字幕文件")
            return []
        
        print(f"\n🔄 找到 {len(vtt_files)} 个VTT字幕文件，开始转换为纯文本...")
        
        converted_files = []
        for vtt_file in vtt_files:
            try:
                # 生成纯文本文件名
                txt_file = os.path.splitext(vtt_file)[0] + '.txt'
                
                # 转换VTT到纯文本
                result_file = convert_vtt_to_text(vtt_file, txt_file)
                converted_files.append(result_file)
                
            except Exception as e:
                print(f"❌ 转换失败 {os.path.basename(vtt_file)}: {e}")
        
        if converted_files:
            print(f"\n✅ 成功转换 {len(converted_files)} 个字幕文件为纯文本格式")
            for txt_file in converted_files:
                print(f"   📄 {os.path.basename(txt_file)}")
        
        return converted_files
        
    except ImportError:
        print("❌ VTT转换模块未找到，请确保vtt_to_text_converter.py存在")
        return []
    except Exception as e:
        print(f"❌ VTT转换过程出错: {e}")
        return []

def check_and_install_ytdlp():
    """检查并安装yt-dlp库"""
    try:
        import yt_dlp
        print("✓ yt-dlp已安装")
        return True
    except ImportError:
        print("yt-dlp未安装，正在安装...")
        try:
            # 优先使用uv，如果不可用则回退到pip
            try:
                subprocess.check_call(["uv", "add", "yt-dlp"])
                print("✓ yt-dlp安装成功 (使用uv)")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("uv不可用，尝试使用pip...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
                print("✓ yt-dlp安装成功 (使用pip)")
                return True
        except subprocess.CalledProcessError:
            print("❌ yt-dlp安装失败，请手动安装: uv add yt-dlp 或 pip install yt-dlp")
            return False

def download_video(url, output_path=None, use_cookies=True, browser='chrome', 
                  quality='720p', audio_only=False, playlist=False, 
                  extract_audio=False, audio_format='mp3'):
    """下载YouTube视频
    
    Args:
        url: YouTube视频链接
        output_path: 输出目录路径
        use_cookies: 是否使用浏览器cookies
        browser: 浏览器类型
        quality: 视频质量 ('720p', '1080p', 'best', 'worst')
        audio_only: 是否只下载音频
        playlist: 是否下载整个播放列表
        extract_audio: 是否提取音频文件
        audio_format: 音频格式 ('mp3', 'aac', 'flac', 'wav')
    """
    try:
        import yt_dlp
    except ImportError:
        print("❌ yt-dlp未安装")
        return False
    
    # 设置下载路径
    if output_path is None:
        output_path = os.path.dirname(os.path.abspath(__file__))
    
    # 确保输出目录存在
    os.makedirs(output_path, exist_ok=True)
    
    # 根据质量设置格式选择器
    if audio_only:
        format_selector = 'bestaudio/best'
        output_template = '%(title)s.%(ext)s'
    elif quality == '720p':
        format_selector = 'best[height<=720]/best'
        output_template = '%(title)s.%(ext)s'
    elif quality == '1080p':
        format_selector = 'best[height<=1080]/best'
        output_template = '%(title)s.%(ext)s'
    elif quality == 'best':
        format_selector = 'best'
        output_template = '%(title)s.%(ext)s'
    elif quality == 'worst':
        format_selector = 'worst'
        output_template = '%(title)s.%(ext)s'
    else:
        format_selector = 'best[height<=720]/best'
        output_template = '%(title)s.%(ext)s'
    
    # 如果是播放列表，调整输出模板
    if playlist:
        output_template = '%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s'
    
    # yt-dlp配置
    ydl_opts = {
        'outtmpl': os.path.join(output_path, output_template),
        'format': format_selector,
        'writesubtitles': True,  # 下载字幕
        'writeautomaticsub': True,  # 下载自动生成的字幕
        'subtitleslangs': ['en', 'zh', 'zh-CN'],  # 字幕语言
        'extractor_retries': 3,  # 重试次数
        'fragment_retries': 3,  # 片段重试次数
        'ignoreerrors': False,  # 遇到错误时停止
        'no_warnings': False,  # 显示警告
        'extractaudio': extract_audio,  # 是否提取音频
    }
    
    # 如果需要提取音频，添加后处理选项
    if extract_audio:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192',
        }]
    
    # 播放列表设置
    if not playlist:
        ydl_opts['noplaylist'] = True
    
    # 添加cookie支持（如果启用）
    if use_cookies:
        try:
            ydl_opts['cookiesfrombrowser'] = (browser,)
            print(f"✓ 已启用从{browser}浏览器导入cookies")
        except Exception as e:
            print(f"⚠️ 无法从{browser}导入cookies，将尝试无cookie下载: {e}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"正在下载: {url}")
            print(f"保存路径: {output_path}")
            
            # 获取视频信息
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            print(f"视频标题: {title}")
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                print(f"视频时长: {minutes}:{seconds:02d}")
            
            # 下载视频
            ydl.download([url])
            print("✓ 下载完成！")
            return True
            
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")
        return False

def get_video_info(url, info_type, use_cookies=True, browser='chrome'):
    """
    获取视频信息而不下载
    Args:
        url: 视频链接
        info_type: 信息类型 ('title', 'description', 'formats')
        use_cookies: 是否使用cookies
        browser: 浏览器类型
    """
    try:
        import yt_dlp
    except ImportError:
        print("❌ yt-dlp未安装")
        return None
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    # 添加cookies支持
    if use_cookies:
        try:
            ydl_opts['cookiesfrombrowser'] = (browser, None, None, None)
        except Exception as e:
            print(f"⚠️ 无法从{browser}导入cookies: {e}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info_type == 'title':
                return info.get('title', 'Unknown')
            elif info_type == 'description':
                return info.get('description', 'No description available')
            elif info_type == 'formats':
                formats = info.get('formats', [])
                return formats
            else:
                return info
                
    except Exception as e:
        print(f"❌ 获取视频信息失败: {str(e)}")
        return None

def list_video_formats(url, use_cookies=True, browser='chrome'):
    """列出视频的可用格式"""
    formats = get_video_info(url, 'formats', use_cookies, browser)
    if not formats:
        return
    
    print("\n可用的视频格式:")
    print("-" * 80)
    print(f"{'格式ID':<10} {'扩展名':<8} {'分辨率':<12} {'文件大小':<12} {'编码':<15} {'说明'}")
    print("-" * 80)
    
    for fmt in formats:
        format_id = fmt.get('format_id', 'N/A')
        ext = fmt.get('ext', 'N/A')
        resolution = fmt.get('resolution', 'N/A')
        filesize = fmt.get('filesize')
        if filesize:
            filesize_mb = f"{filesize / 1024 / 1024:.1f}MB"
        else:
            filesize_mb = 'N/A'
        vcodec = fmt.get('vcodec', 'N/A')
        acodec = fmt.get('acodec', 'N/A')
        format_note = fmt.get('format_note', '')
        
        # 简化编码信息
        codec_info = f"{vcodec[:12]}" if vcodec != 'none' else f"audio:{acodec[:8]}"
        
        print(f"{format_id:<10} {ext:<8} {resolution:<12} {filesize_mb:<12} {codec_info:<15} {format_note}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='YouTube视频下载器 - 基于yt-dlp的功能丰富的下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s "https://www.youtube.com/watch?v=VIDEO_ID"
  %(prog)s -q 1080p --extract-audio --audio-format mp3 "URL"
  %(prog)s --playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"
  %(prog)s --audio-only "URL"
        """
    )
    
    # 基本参数
    parser.add_argument('url', nargs='?', help='YouTube视频或播放列表链接')
    parser.add_argument('-o', '--output', help='输出目录路径')
    
    # Cookie和浏览器设置
    parser.add_argument('--no-cookies', action='store_true', help='禁用cookie导入')
    parser.add_argument('--browser', default='chrome', 
                       choices=['chrome', 'firefox', 'safari', 'edge'], 
                       help='选择浏览器导入cookies (默认: chrome)')
    
    # 视频质量和格式
    parser.add_argument('-q', '--quality', default='720p',
                       choices=['720p', '1080p', 'best', 'worst'],
                       help='视频质量 (默认: 720p)')
    
    # 音频选项
    parser.add_argument('--audio-only', action='store_true',
                       help='只下载音频（最佳音频质量）')
    parser.add_argument('--extract-audio', action='store_true',
                       help='下载视频并提取音频文件')
    parser.add_argument('--audio-format', default='mp3',
                       choices=['mp3', 'aac', 'flac', 'wav'],
                       help='音频格式 (默认: mp3)')
    
    # 播放列表选项
    parser.add_argument('--playlist', action='store_true',
                       help='下载整个播放列表')
    
    # 信息选项
    parser.add_argument('--list-formats', action='store_true',
                       help='列出可用的视频格式而不下载')
    parser.add_argument('--get-title', action='store_true',
                       help='获取视频标题而不下载')
    parser.add_argument('--get-description', action='store_true',
                       help='获取视频描述而不下载')
    
    # VTT转换选项
    parser.add_argument('--convert-vtt-to-text', action='store_true',
                       help='自动将下载的VTT字幕转换为按时间轴标注的纯文本格式')
    
    args = parser.parse_args()
    
    # 检查并安装yt-dlp
    if not check_and_install_ytdlp():
        return
    
    # 获取视频URL
    if args.url:
        video_url = args.url
    else:
        video_url = input("请输入YouTube视频链接: ").strip()
    
    if not video_url:
        print("❌ 请提供有效的YouTube链接")
        return
    
    # 验证URL
    if 'youtube.com' not in video_url and 'youtu.be' not in video_url:
        print("❌ 请提供有效的YouTube链接")
        return
    
    # 处理信息获取选项（不下载）
    use_cookies = not args.no_cookies
    
    if args.list_formats:
        print("正在获取视频格式信息...")
        list_video_formats(video_url, use_cookies, args.browser)
        return
    
    if args.get_title:
        print("正在获取视频标题...")
        title = get_video_info(video_url, 'title', use_cookies, args.browser)
        if title:
            print(f"视频标题: {title}")
        return
    
    if args.get_description:
        print("正在获取视频描述...")
        description = get_video_info(video_url, 'description', use_cookies, args.browser)
        if description:
            print(f"视频描述:\n{description}")
        return
    
    # 设置输出路径
    output_path = args.output if args.output else os.path.dirname(os.path.abspath(__file__))
    
    # 参数验证和提示
    if args.audio_only and args.extract_audio:
        print("⚠️ --audio-only 和 --extract-audio 不能同时使用，将使用 --audio-only")
        args.extract_audio = False
    
    # 显示下载配置
    print("\n📋 下载配置:")
    print(f"   视频质量: {args.quality}")
    if args.audio_only:
        print("   模式: 仅音频")
    elif args.extract_audio:
        print(f"   模式: 视频+音频提取 ({args.audio_format})")
    else:
        print("   模式: 视频+字幕")
    
    if args.playlist:
        print("   播放列表: 是")
    else:
        print("   播放列表: 否")
    
    print(f"   Cookie支持: {'是' if not args.no_cookies else '否'}")
    if not args.no_cookies:
        print(f"   浏览器: {args.browser}")
    print(f"   输出路径: {output_path}")
    print()
    
    # 下载视频
    use_cookies = not args.no_cookies
    success = download_video(
        url=video_url,
        output_path=output_path,
        use_cookies=use_cookies,
        browser=args.browser,
        quality=args.quality,
        audio_only=args.audio_only,
        playlist=args.playlist,
        extract_audio=args.extract_audio,
        audio_format=args.audio_format
    )
    
    if success:
        print(f"\n✅ 下载完成！文件已保存到: {output_path}")
        if args.extract_audio:
            print(f"   音频文件格式: {args.audio_format}")
        
        # 自动转换VTT为纯文本（如果启用）
        if args.convert_vtt_to_text:
            convert_vtt_to_text_auto(output_path)
    else:
        print("\n❌ 下载失败，请检查链接是否正确或网络连接")

if __name__ == "__main__":
    main()