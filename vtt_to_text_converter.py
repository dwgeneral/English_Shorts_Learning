#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VTT字幕转纯文本工具
将VTT字幕文件转换为按时间轴标注的纯文本格式
"""

import re
import argparse
import sys
from pathlib import Path
from typing import List, Tuple

def parse_vtt_time(time_str: str) -> float:
    """解析VTT时间格式为秒数"""
    # 格式: 00:00:00.000 或 00:00.000
    time_str = time_str.strip()
    
    if '.' in time_str:
        time_part, ms_part = time_str.split('.')
        ms = float('0.' + ms_part)
    else:
        time_part = time_str
        ms = 0
    
    time_parts = time_part.split(':')
    
    if len(time_parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = map(int, time_parts)
    elif len(time_parts) == 2:  # MM:SS
        hours = 0
        minutes, seconds = map(int, time_parts)
    else:
        raise ValueError(f"无法解析时间格式: {time_str}")
    
    return hours * 3600 + minutes * 60 + seconds + ms

def format_time_for_text(seconds: float) -> str:
    """将秒数格式化为可读的时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def clean_subtitle_text(text: str) -> str:
    """清理字幕文本，移除HTML标签和特殊标记"""
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 移除VTT样式标记
    text = re.sub(r'\{[^}]+\}', '', text)
    # 移除多余的空白字符
    text = ' '.join(text.split())
    return text.strip()

def merge_continuous_subtitles(subtitles: List[Tuple[float, float, str]]) -> List[Tuple[float, float, str]]:
    """合并连续的字幕，创建完整的句子段落"""
    if not subtitles:
        return []
    
    merged = []
    current_start, current_end, current_text = subtitles[0]
    current_text = clean_subtitle_text(current_text)
    
    for i in range(1, len(subtitles)):
        start_time, end_time, text = subtitles[i]
        clean_text = clean_subtitle_text(text)
        
        # 检查时间间隔
        time_gap = start_time - current_end
        
        # 检查文本连续性
        words_current = current_text.split()
        words_new = clean_text.split()
        
        # 如果时间间隔小于1秒，或者新文本是当前文本的延续
        should_merge = False
        
        if time_gap < 1.0:  # 时间间隔很小
            should_merge = True
        elif len(words_current) > 0 and len(words_new) > 0:
            # 检查是否有重叠的词汇（表示连续性）
            last_words = words_current[-3:] if len(words_current) >= 3 else words_current
            first_words = words_new[:3] if len(words_new) >= 3 else words_new
            
            # 如果有重叠词汇，说明是连续的
            overlap = set(last_words) & set(first_words)
            if len(overlap) > 0:
                should_merge = True
        
        if should_merge:
            # 合并文本，避免重复
            combined_text = current_text + " " + clean_text
            # 简单去重：如果新文本完全包含在当前文本中，不添加
            if clean_text not in current_text:
                # 检查重叠词汇并智能合并
                words_current = current_text.split()
                words_new = clean_text.split()
                
                # 找到重叠部分
                max_overlap = 0
                overlap_start = 0
                
                for j in range(min(len(words_current), len(words_new))):
                    if words_current[-(j+1):] == words_new[:j+1]:
                        max_overlap = j + 1
                        overlap_start = j + 1
                
                if max_overlap > 0:
                    # 有重叠，合并时去除重复部分
                    current_text = current_text + " " + " ".join(words_new[overlap_start:])
                else:
                    # 无重叠，直接连接
                    current_text = current_text + " " + clean_text
            
            current_end = end_time
        else:
            # 保存当前字幕，开始新的字幕
            if current_text.strip():
                merged.append((current_start, current_end, current_text.strip()))
            current_start, current_end, current_text = start_time, end_time, clean_text
    
    # 添加最后一个字幕
    if current_text.strip():
        merged.append((current_start, current_end, current_text.strip()))
    
    return merged

def add_punctuation_by_timing(subtitles: List[Tuple[float, float, str]]) -> str:
    """根据时间间隔智能添加标点符号"""
    # 首先合并连续的字幕
    merged_subtitles = merge_continuous_subtitles(subtitles)
    
    result = []
    
    for i, (start_time, end_time, text) in enumerate(merged_subtitles):
        if not text.strip():
            continue
            
        # 添加时间标记
        time_mark = f"[{format_time_for_text(start_time)}]"
        
        # 判断是否需要添加标点符号
        if i < len(merged_subtitles) - 1:
            next_start = merged_subtitles[i + 1][0]
            gap = next_start - end_time
            
            # 根据时间间隔添加标点
            if gap > 2.0:  # 超过2秒的停顿，添加句号
                if not text.endswith(('.', '!', '?', '。', '！', '？')):
                    text += '.'
            elif gap > 1.0:  # 1-2秒的停顿，添加逗号
                if not text.endswith((',', '.', '!', '?', '，', '。', '！', '？')):
                    text += ','
        else:
            # 最后一句，添加句号
            if not text.endswith(('.', '!', '?', '。', '！', '？')):
                text += '.'
        
        result.append(f"{time_mark} {text}")
    
    return '\n'.join(result)

def convert_vtt_to_text(vtt_file: str, output_file: str = None) -> str:
    """将VTT文件转换为纯文本格式"""
    vtt_path = Path(vtt_file)
    
    if not vtt_path.exists():
        raise FileNotFoundError(f"VTT文件不存在: {vtt_file}")
    
    # 生成输出文件名
    if output_file is None:
        output_file = vtt_path.with_suffix('.txt').name
    
    print(f"🔄 开始转换: {vtt_path.name} -> {output_file}")
    
    # 读取VTT文件
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析VTT内容
    subtitles = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 跳过空行和WEBVTT标记
        if not line or line.startswith('WEBVTT') or line.startswith('NOTE'):
            i += 1
            continue
        
        # 检查是否是时间戳行
        if '-->' in line:
            time_match = re.match(r'([\d:.]+)\s*-->\s*([\d:.]+)', line)
            if time_match:
                start_str, end_str = time_match.groups()
                start_time = parse_vtt_time(start_str)
                end_time = parse_vtt_time(end_str)
                
                # 收集字幕文本
                subtitle_lines = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    subtitle_lines.append(lines[i].strip())
                    i += 1
                
                if subtitle_lines:
                    subtitle_text = ' '.join(subtitle_lines)
                    subtitles.append((start_time, end_time, subtitle_text))
        
        i += 1
    
    print(f"📝 解析完成，共 {len(subtitles)} 条字幕")
    
    # 转换为带标点的文本
    text_content = add_punctuation_by_timing(subtitles)
    
    # 写入文件
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    print(f"✅ 转换成功！输出文件: {output_file}")
    return output_file

def batch_convert_vtt_to_text(directory: str = '.') -> List[str]:
    """批量转换目录下的所有VTT文件"""
    dir_path = Path(directory)
    vtt_files = list(dir_path.glob('*.vtt'))
    
    if not vtt_files:
        print("❌ 当前目录下没有找到VTT文件")
        return []
    
    print(f"🔍 找到 {len(vtt_files)} 个VTT文件")
    
    converted_files = []
    for vtt_file in vtt_files:
        try:
            output_file = convert_vtt_to_text(str(vtt_file))
            converted_files.append(output_file)
        except Exception as e:
            print(f"❌ 转换失败 {vtt_file.name}: {e}")
    
    print(f"\n🎉 批量转换完成！成功转换 {len(converted_files)} 个文件")
    return converted_files

def main():
    parser = argparse.ArgumentParser(
        description='VTT字幕转纯文本工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s subtitle.vtt                    # 转换单个文件
  %(prog)s subtitle.vtt -o output.txt      # 指定输出文件
  %(prog)s --batch                         # 批量转换当前目录
        """
    )
    
    parser.add_argument('vtt_file', nargs='?', help='输入的VTT字幕文件路径')
    parser.add_argument('-o', '--output', help='输出的文本文件路径（可选）')
    parser.add_argument('--batch', action='store_true', help='批量转换当前目录下的所有VTT文件')
    
    args = parser.parse_args()
    
    try:
        if args.batch:
            batch_convert_vtt_to_text()
        elif args.vtt_file:
            convert_vtt_to_text(args.vtt_file, args.output)
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()