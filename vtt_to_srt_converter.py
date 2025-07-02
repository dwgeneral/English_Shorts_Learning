#!/usr/bin/env python3
"""
VTT到SRT字幕格式转换工具
将WebVTT (.vtt) 字幕文件转换为SubRip (.srt) 格式
"""

import re
import os
import sys
import argparse
from typing import List, Dict

class VTTToSRTConverter:
    """VTT到SRT转换器"""
    
    def __init__(self, vtt_file: str, srt_file: str = None):
        self.vtt_file = vtt_file
        self.srt_file = srt_file or self._get_srt_filename(vtt_file)
        
    def _get_srt_filename(self, vtt_file: str) -> str:
        """根据VTT文件名生成SRT文件名"""
        base_name = os.path.splitext(vtt_file)[0]
        return f"{base_name}.srt"
    
    def _parse_vtt_time(self, time_str: str) -> str:
        """将VTT时间格式转换为SRT时间格式"""
        # VTT格式: 00:00:00.040 或 00:00:00.040
        # SRT格式: 00:00:00,040
        return time_str.replace('.', ',')
    
    def _clean_text(self, text: str) -> str:
        """清理字幕文本，移除VTT特有的标记"""
        # 移除位置和对齐信息
        text = re.sub(r'align:start position:\d+%', '', text)
        text = re.sub(r'align:\w+', '', text)
        text = re.sub(r'position:\d+%', '', text)
        
        # 移除VTT的时间标记 <00:00:00.480><c> ... </c>
        text = re.sub(r'<[^>]*>', '', text)
        
        # 移除多余的空格
        text = ' '.join(text.split())
        
        return text.strip()
    
    def parse_vtt(self) -> List[Dict]:
        """解析VTT文件"""
        subtitles = []
        
        try:
            with open(self.vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"错误: 找不到文件 {self.vtt_file}")
            return []
        except UnicodeDecodeError:
            print(f"错误: 无法读取文件 {self.vtt_file}，请检查文件编码")
            return []
        
        # 分割成块
        blocks = content.split('\n\n')
        subtitle_index = 1
        
        for block in blocks:
            block = block.strip()
            if not block or block.startswith('WEBVTT') or block.startswith('Kind:') or block.startswith('Language:'):
                continue
            
            lines = block.split('\n')
            if len(lines) < 2:
                continue
            
            # 查找时间行
            time_line = None
            text_lines = []
            
            for line in lines:
                if '-->' in line:
                    time_line = line
                elif line.strip() and not line.startswith('NOTE'):
                    text_lines.append(line)
            
            if not time_line or not text_lines:
                continue
            
            # 解析时间
            time_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', time_line)
            if not time_match:
                continue
            
            start_time = self._parse_vtt_time(time_match.group(1))
            end_time = self._parse_vtt_time(time_match.group(2))
            
            # 合并文本行并清理
            text = ' '.join(text_lines)
            text = self._clean_text(text)
            
            if text:  # 只添加非空文本
                subtitles.append({
                    'index': subtitle_index,
                    'start': start_time,
                    'end': end_time,
                    'text': text
                })
                subtitle_index += 1
        
        return subtitles
    
    def write_srt(self, subtitles: List[Dict]) -> bool:
        """写入SRT文件"""
        try:
            with open(self.srt_file, 'w', encoding='utf-8') as f:
                for subtitle in subtitles:
                    f.write(f"{subtitle['index']}\n")
                    f.write(f"{subtitle['start']} --> {subtitle['end']}\n")
                    f.write(f"{subtitle['text']}\n\n")
            return True
        except Exception as e:
            print(f"错误: 无法写入文件 {self.srt_file}: {e}")
            return False
    
    def convert(self) -> bool:
        """执行转换"""
        print(f"🔄 开始转换: {self.vtt_file} -> {self.srt_file}")
        
        # 解析VTT文件
        print("📝 解析VTT文件...")
        subtitles = self.parse_vtt()
        
        if not subtitles:
            print("❌ 未找到有效的字幕内容")
            return False
        
        print(f"✓ 解析完成，共 {len(subtitles)} 条字幕")
        
        # 写入SRT文件
        print("💾 写入SRT文件...")
        if self.write_srt(subtitles):
            print(f"✅ 转换成功！输出文件: {self.srt_file}")
            return True
        else:
            return False

def main():
    parser = argparse.ArgumentParser(description='VTT到SRT字幕格式转换工具')
    parser.add_argument('vtt_file', help='输入的VTT字幕文件路径')
    parser.add_argument('-o', '--output', help='输出的SRT文件路径（可选）')
    parser.add_argument('--batch', action='store_true', help='批量转换当前目录下的所有VTT文件')
    
    args = parser.parse_args()
    
    if args.batch:
        # 批量转换模式
        vtt_files = [f for f in os.listdir('.') if f.endswith('.vtt')]
        if not vtt_files:
            print("❌ 当前目录下没有找到VTT文件")
            return
        
        print(f"🔍 找到 {len(vtt_files)} 个VTT文件")
        success_count = 0
        
        for vtt_file in vtt_files:
            print(f"\n处理文件: {vtt_file}")
            converter = VTTToSRTConverter(vtt_file)
            if converter.convert():
                success_count += 1
        
        print(f"\n🎉 批量转换完成！成功转换 {success_count}/{len(vtt_files)} 个文件")
    else:
        # 单文件转换模式
        if not os.path.exists(args.vtt_file):
            print(f"❌ 错误: 文件不存在: {args.vtt_file}")
            sys.exit(1)
        
        converter = VTTToSRTConverter(args.vtt_file, args.output)
        if converter.convert():
            print("\n🎉 转换完成！")
        else:
            print("\n❌ 转换失败")
            sys.exit(1)

if __name__ == '__main__':
    main()