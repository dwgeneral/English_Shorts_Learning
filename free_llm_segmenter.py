#!/usr/bin/env python3
"""
免费LLM视频分段工具
支持多种免费LLM API进行智能视频分段
"""

import re
import os
import sys
import json
import argparse
import subprocess
from typing import List, Dict, Tuple, Optional
import requests
from video_segmenter import VTTParser, VideoSegmenter

class FreeLLMAnalyzer:
    """支持多种免费LLM的分析器"""
    
    def __init__(self, provider: str = "rule", api_key: str = None, model: str = None, base_url: str = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        
    def analyze_segments(self, subtitles: List[Dict], target_duration: int = 35) -> List[float]:
        """分析字幕内容，返回分段时间点（秒）"""
        if self.provider == "rule":
            return self._rule_based_segmentation(subtitles, target_duration)
        elif self.provider == "ollama":
            return self._ollama_segmentation(subtitles, target_duration)
        elif self.provider == "huggingface":
            return self._huggingface_segmentation(subtitles, target_duration)
        elif self.provider == "openai":
            return self._openai_segmentation(subtitles, target_duration)
        elif self.provider == "qwen":
            return self._qwen_segmentation(subtitles, target_duration)
        else:
            print(f"不支持的提供商: {self.provider}，使用基于规则的分段")
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
    
    def _ollama_segmentation(self, subtitles: List[Dict], target_duration: int) -> List[float]:
        """使用Ollama本地模型进行分段"""
        try:
            # 准备文本
            text_with_time = ""
            for sub in subtitles[:50]:  # 限制文本长度
                text_with_time += f"[{sub['start']}] {sub['text']} "
            
            prompt = f"""
请分析以下带时间戳的视频字幕内容，找出合适的分段点。每段应该在{target_duration-5}到{target_duration+5}秒之间。

分段原则：
1. 在自然的话题转换点分段
2. 在完整句子结束后分段
3. 避免在句子中间分段
4. 考虑内容的逻辑连贯性

字幕内容：
{text_with_time}

请只返回JSON格式的分段时间点，格式如下：
{{"segments": ["00:00:35.000", "00:01:10.000"]}}
"""
            
            # 调用Ollama API
            response = requests.post(
                f"{self.base_url or 'http://localhost:11434'}/api/generate",
                json={
                    "model": self.model or "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '')
                return self._parse_time_segments(content)
            else:
                raise Exception(f"Ollama API错误: {response.status_code}")
                
        except Exception as e:
            print(f"Ollama分析失败，使用基于规则的分段: {e}")
            return self._rule_based_segmentation(subtitles, target_duration)
    
    def _huggingface_segmentation(self, subtitles: List[Dict], target_duration: int) -> List[float]:
        """使用Hugging Face Inference API进行分段"""
        try:
            # 准备文本
            text_with_time = ""
            for sub in subtitles[:30]:  # 限制文本长度
                text_with_time += f"[{sub['start']}] {sub['text']} "
            
            prompt = f"""Analyze this video transcript and suggest segment breakpoints every {target_duration} seconds at natural conversation breaks. Return only time codes in format HH:MM:SS.mmm:\n\n{text_with_time}"""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 使用免费的文本生成模型
            model_name = self.model or "microsoft/DialoGPT-medium"
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_name}",
                headers=headers,
                json={"inputs": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    content = result[0].get('generated_text', '')
                    return self._parse_time_segments(content)
            
            raise Exception(f"Hugging Face API错误: {response.status_code}")
            
        except Exception as e:
            print(f"Hugging Face分析失败，使用基于规则的分段: {e}")
            return self._rule_based_segmentation(subtitles, target_duration)
    
    def _openai_segmentation(self, subtitles: List[Dict], target_duration: int) -> List[float]:
        """使用OpenAI API进行分段"""
        try:
            # 准备文本
            text_with_time = ""
            for sub in subtitles[:50]:
                text_with_time += f"[{sub['start']}] {sub['text']} "
            
            prompt = f"""
请分析以下带时间戳的视频字幕内容，找出合适的分段点。每段应该在{target_duration-5}到{target_duration+5}秒之间。

分段原则：
1. 在自然的话题转换点分段
2. 在完整句子结束后分段
3. 避免在句子中间分段
4. 考虑内容的逻辑连贯性

字幕内容：
{text_with_time}

请返回JSON格式的分段时间点，例如：
{{"segments": ["00:00:35.000", "00:01:10.000"]}}
"""
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model or 'gpt-3.5-turbo',
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
                return self._parse_time_segments(content)
            
            raise Exception(f"OpenAI API错误: {response.status_code}")
            
        except Exception as e:
            print(f"OpenAI分析失败，使用基于规则的分段: {e}")
            return self._rule_based_segmentation(subtitles, target_duration)
    
    def _qwen_segmentation(self, subtitles: List[Dict], target_duration: int) -> List[float]:
        """使用通义千问API进行分段"""
        try:
            # 准备文本
            text_with_time = ""
            for sub in subtitles[:40]:
                text_with_time += f"[{sub['start']}] {sub['text']} "
            
            prompt = f"""
请分析以下带时间戳的视频字幕内容，找出合适的分段点。每段应该在{target_duration-5}到{target_duration+5}秒之间。

分段原则：
1. 在自然的话题转换点分段
2. 在完整句子结束后分段
3. 避免在句子中间分段
4. 考虑内容的逻辑连贯性

字幕内容：
{text_with_time}

请返回JSON格式的分段时间点，例如：
{{"segments": ["00:00:35.000", "00:01:10.000"]}}
"""
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model or 'qwen-turbo',
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的视频编辑助手，擅长分析内容并找到合适的分段点。'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3
            }
            
            # 通义千问API地址
            api_url = self.base_url or 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
            
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['output']['text']
                return self._parse_time_segments(content)
            
            raise Exception(f"通义千问API错误: {response.status_code}")
            
        except Exception as e:
            print(f"通义千问分析失败，使用基于规则的分段: {e}")
            return self._rule_based_segmentation(subtitles, target_duration)
    
    def _parse_time_segments(self, content: str) -> List[float]:
        """从LLM响应中解析时间段"""
        segments = []
        
        # 尝试解析JSON
        try:
            # 查找JSON部分
            json_match = re.search(r'\{[^}]*"segments"[^}]*\}', content)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                for time_str in data.get('segments', []):
                    segments.append(self._time_to_seconds(time_str))
                return segments
        except json.JSONDecodeError:
            pass
        
        # 如果JSON解析失败，尝试从文本中提取时间
        time_pattern = r'\d{2}:\d{2}:\d{2}\.\d{3}'
        times = re.findall(time_pattern, content)
        for time_str in times:
            segments.append(self._time_to_seconds(time_str))
        
        return segments

def main():
    parser = argparse.ArgumentParser(description='免费LLM智能视频分段工具')
    parser.add_argument('video', help='输入视频文件路径')
    parser.add_argument('vtt', help='VTT字幕文件路径')
    parser.add_argument('-o', '--output', default='segments', help='输出目录（默认: segments）')
    parser.add_argument('-d', '--duration', type=int, default=35, help='目标片段时长（秒，默认: 35）')
    parser.add_argument('--provider', choices=['rule', 'ollama', 'huggingface', 'openai', 'qwen'], 
                       default='rule', help='LLM提供商（默认: rule）')
    parser.add_argument('--api-key', help='API密钥（某些提供商需要）')
    parser.add_argument('--model', help='模型名称')
    parser.add_argument('--base-url', help='API基础URL（可选）')
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
    
    print(f"🎬 开始智能视频分段（使用 {args.provider} 提供商）...")
    
    # 解析VTT文件
    print("📝 解析字幕文件...")
    parser_vtt = VTTParser(args.vtt)
    subtitles = parser_vtt.parse()
    print(f"✓ 解析完成，共 {len(subtitles)} 条字幕")
    
    # 分析分段点
    print(f"🤖 使用 {args.provider} 分析分段点...")
    analyzer = FreeLLMAnalyzer(args.provider, args.api_key, args.model, args.base_url)
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
    
    # 显示使用的提供商信息
    if args.provider != 'rule':
        print(f"\n💡 使用了 {args.provider} 提供商进行智能分析")
        if args.provider == 'ollama':
            print("   确保Ollama服务正在运行: ollama serve")
        elif args.provider in ['huggingface', 'openai', 'qwen']:
            print("   如需更好效果，请提供有效的API密钥")

if __name__ == '__main__':
    main()