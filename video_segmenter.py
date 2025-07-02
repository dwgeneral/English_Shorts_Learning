#!/usr/bin/env python3
"""
智能视频分段工具
基于VTT字幕内容使用LLM分析合适的断点，然后用ffmpeg进行分段
"""

import re
import os
import sys
import json
import argparse
import subprocess
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import requests

class VTTParser:
    """VTT字幕文件解析器"""
    
    def __init__(self, vtt_file: str):
        self.vtt_file = vtt_file
        self.subtitles = []
        
    def parse(self) -> List[Dict]:
        """解析VTT文件，返回字幕列表"""
        with open(self.vtt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配时间戳和文本的正则表达式
        pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3}).*?\n(.*?)(?=\n\n|\n\d{2}:|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            start_time = match[0]
            end_time = match[1]
            text = match[2].strip()
            
            # 清理文本，移除HTML标签和时间戳
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}', '', text)
            text = re.sub(r'<c>|</c>', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if text and text not in ['[Music]', ' ']:
                self.subtitles.append({
                    'start': start_time,
                    'end': end_time,
                    'text': text
                })
        
        return self.subtitles
    
    def time_to_seconds(self, time_str: str) -> float:
        """将时间字符串转换为秒数"""
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
    
    def seconds_to_time(self, seconds: float) -> str:
        """将秒数转换为时间字符串"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}"

class LLMAnalyzer:
    """使用LLM分析字幕内容找到合适的分段点"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        
    def analyze_segments(self, subtitles: List[Dict], target_duration: int = 35) -> List[float]:
        """分析字幕内容，返回分段时间点（秒）"""
        # 将字幕文本合并为连续文本
        full_text = ""
        time_mapping = []
        
        for sub in subtitles:
            start_seconds = self._time_to_seconds(sub['start'])
            full_text += f"[{sub['start']}] {sub['text']} "
            time_mapping.append((start_seconds, len(full_text)))
        
        # 如果没有API密钥，使用基于规则的分段
        if not self.api_key:
            return self._rule_based_segmentation(subtitles, target_duration)
        
        # 使用LLM分析
        try:
            return self._llm_based_segmentation(full_text, time_mapping, target_duration)
        except Exception as e:
            print(f"LLM分析失败，使用基于规则的分段: {e}")
            return self._rule_based_segmentation(subtitles, target_duration)
    
    def _time_to_seconds(self, time_str: str) -> float:
        """将时间字符串转换为秒数"""
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
    
    def _rule_based_segmentation(self, subtitles: List[Dict], target_duration: int) -> List[float]:
        """基于规则的分段方法"""
        segments = []
        current_start = 0
        
        for i, sub in enumerate(subtitles):
            current_time = self._time_to_seconds(sub['start'])
            
            # 如果当前段落已经达到目标时长
            if current_time - current_start >= target_duration:
                # 寻找合适的断点（句号、问号、感叹号后）
                text = sub['text']
                if any(punct in text for punct in ['.', '?', '!', '。', '？', '！']):
                    segments.append(current_time)
                    current_start = current_time
                # 或者在停顿较长的地方分段
                elif i < len(subtitles) - 1:
                    next_start = self._time_to_seconds(subtitles[i + 1]['start'])
                    current_end = self._time_to_seconds(sub['end'])
                    if next_start - current_end > 1.0:  # 停顿超过1秒
                        segments.append(current_time)
                        current_start = current_time
        
        return segments
    
    def _llm_based_segmentation(self, text: str, time_mapping: List[Tuple], target_duration: int) -> List[float]:
        """使用LLM进行智能分段"""
        prompt = f"""
请分析以下带时间戳的视频字幕内容，找出合适的分段点。每段应该在{target_duration-5}到{target_duration+5}秒之间。

分段原则：
1. 在自然的话题转换点分段
2. 在完整句子结束后分段
3. 避免在句子中间分段
4. 考虑内容的逻辑连贯性

字幕内容：
{text[:2000]}...

请返回JSON格式的分段时间点（格式：HH:MM:SS.mmm），例如：
{{"segments": ["00:00:35.000", "00:01:10.000", "00:01:45.000"]}}
"""
        
        # 这里可以替换为不同的免费LLM API
        # 示例使用OpenAI API（需要API密钥）
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': '你是一个专业的视频编辑助手，擅长分析内容并找到合适的分段点。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 解析JSON响应
            try:
                segments_data = json.loads(content)
                segments = []
                for time_str in segments_data.get('segments', []):
                    segments.append(self._time_to_seconds(time_str))
                return segments
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试从文本中提取时间
                time_pattern = r'\d{2}:\d{2}:\d{2}\.\d{3}'
                times = re.findall(time_pattern, content)
                return [self._time_to_seconds(t) for t in times]
        
        raise Exception(f"API请求失败: {response.status_code}")

class VideoSegmenter:
    """视频分段器"""
    
    def __init__(self, video_file: str, output_dir: str = "segments"):
        self.video_file = video_file
        self.output_dir = output_dir
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    def segment_video(self, breakpoints: List[float]) -> List[str]:
        """根据断点分段视频"""
        output_files = []
        
        # 添加开始和结束时间点
        all_points = [0.0] + sorted(breakpoints) + [self._get_video_duration()]
        
        for i in range(len(all_points) - 1):
            start_time = all_points[i]
            end_time = all_points[i + 1]
            duration = end_time - start_time
            
            # 跳过太短的片段
            if duration < 10:
                continue
            
            output_file = os.path.join(self.output_dir, f"segment_{i+1:03d}.mp4")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', self.video_file,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c', 'copy',
                output_file
            ]
            
            print(f"正在生成片段 {i+1}: {start_time:.1f}s - {end_time:.1f}s ({duration:.1f}s)")
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                output_files.append(output_file)
                print(f"✓ 生成成功: {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"✗ 生成失败: {e}")
        
        return output_files
    
    def _get_video_duration(self) -> float:
        """获取视频总时长"""
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            self.video_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except Exception:
            # 如果ffprobe失败，从VTT文件估算
            return 24 * 60  # 默认24分钟

def main():
    parser = argparse.ArgumentParser(description='智能视频分段工具')
    parser.add_argument('video', help='输入视频文件路径')
    parser.add_argument('vtt', help='VTT字幕文件路径')
    parser.add_argument('-o', '--output', default='segments', help='输出目录（默认: segments）')
    parser.add_argument('-d', '--duration', type=int, default=35, help='目标片段时长（秒，默认: 35）')
    parser.add_argument('--api-key', help='LLM API密钥（可选，不提供则使用基于规则的分段）')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='LLM模型名称（默认: gpt-3.5-turbo）')
    parser.add_argument('--dry-run', action='store_true', help='仅分析分段点，不实际分割视频')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.video):
        print(f"错误: 视频文件不存在: {args.video}")
        sys.exit(1)
    
    if not os.path.exists(args.vtt):
        print(f"错误: VTT文件不存在: {args.vtt}")
        sys.exit(1)
    
    # 检查ffmpeg是否可用
    if not args.dry_run:
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("错误: 未找到ffmpeg，请先安装ffmpeg")
            sys.exit(1)
    
    print("🎬 开始智能视频分段...")
    
    # 解析VTT文件
    print("📝 解析字幕文件...")
    parser_vtt = VTTParser(args.vtt)
    subtitles = parser_vtt.parse()
    print(f"✓ 解析完成，共 {len(subtitles)} 条字幕")
    
    # 分析分段点
    print("🤖 分析分段点...")
    analyzer = LLMAnalyzer(args.api_key, args.model)
    breakpoints = analyzer.analyze_segments(subtitles, args.duration)
    print(f"✓ 分析完成，找到 {len(breakpoints)} 个分段点")
    
    # 显示分段信息
    print("\n📊 分段信息:")
    all_points = [0.0] + sorted(breakpoints)
    for i in range(len(all_points)):
        start = all_points[i]
        end = all_points[i + 1] if i + 1 < len(all_points) else parser_vtt.time_to_seconds(subtitles[-1]['end'])
        duration = end - start
        print(f"  片段 {i+1}: {parser_vtt.seconds_to_time(start)} - {parser_vtt.seconds_to_time(end)} ({duration:.1f}s)")
    
    if args.dry_run:
        print("\n🔍 仅分析模式，未生成视频片段")
        return
    
    # 分割视频
    print("\n✂️ 开始分割视频...")
    segmenter = VideoSegmenter(args.video, args.output)
    output_files = segmenter.segment_video(breakpoints)
    
    print(f"\n🎉 分割完成！生成了 {len(output_files)} 个视频片段:")
    for file in output_files:
        print(f"  - {file}")

if __name__ == '__main__':
    main()