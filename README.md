# YouTube视频下载器

这是一个功能丰富的YouTube视频下载工具，基于Python和yt-dlp库实现，参考了youtube-dl项目的优秀特性。

## 功能特点

- 🎥 下载YouTube视频（支持720p、1080p、最佳、最差质量）
- 🎵 音频下载和提取（MP3、AAC、FLAC、WAV格式）
- 📝 自动下载字幕（英文、中文）
- 📋 播放列表批量下载
- 🔧 自动安装依赖库
- 📁 灵活的文件组织和命名
- 💡 支持命令行和交互式使用
- 🍪 智能Cookie支持，绕过反机器人验证
- 🌐 支持多种浏览器（Chrome、Firefox、Safari、Edge）
- ℹ️ 视频信息查询（标题、描述、格式列表）
- 🔥 字幕烧录功能（将VTT字幕文件烧录到视频中）
- ✂️ 智能视频分段功能（基于字幕内容自动分割视频）
- 🤖 免费LLM智能分段（支持Ollama、Hugging Face等多种免费AI模型）
- 🔄 VTT到SRT字幕格式转换（支持单文件和批量转换）
- 🔄 基于yt-dlp的稳定性和兼容性

## 安装依赖

### 使用uv（推荐）

```bash
# 初始化项目
uv init

# 安装依赖
uv sync
```

### 使用pip（备选）

```bash
pip install -r requirements.txt
```

或者运行脚本时会自动安装依赖（优先使用uv）。

## 使用方法

### 方法1：使用uv运行（推荐）

```bash
# 基本使用
uv run youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 交互式使用
uv run youtube_downloader.py

# 指定输出目录
uv run youtube_downloader.py "URL" -o "/path/to/output"

# 视频质量选择
uv run youtube_downloader.py "URL" -q 1080p
uv run youtube_downloader.py "URL" -q best

# 音频下载
uv run youtube_downloader.py "URL" --audio-only
uv run youtube_downloader.py "URL" --extract-audio --audio-format mp3

# 播放列表下载
uv run youtube_downloader.py "PLAYLIST_URL" --playlist

# 获取视频信息（不下载）
uv run youtube_downloader.py "URL" --get-title
uv run youtube_downloader.py "URL" --get-description
uv run youtube_downloader.py "URL" --list-formats

# Cookie和浏览器设置
uv run youtube_downloader.py "URL" --browser firefox
uv run youtube_downloader.py "URL" --no-cookies

# 组合使用
uv run youtube_downloader.py "URL" -q 1080p --extract-audio --audio-format flac --browser safari

# 字幕烧录功能
uv run subtitle_burner.py video.mp4 subtitles.vtt
uv run subtitle_burner.py video.mp4 subtitles.vtt -o output_with_subs.mp4
uv run subtitle_burner.py video.mp4 subtitles.vtt --font-size 28 --font-color yellow
```

### 方法2：直接使用Python

```bash
# 交互式使用
python youtube_downloader.py

# 命令行参数
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 指定输出目录
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" -o "/path/to/output"

# 使用不同浏览器的cookies
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --browser safari

# 禁用cookie导入
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --no-cookies
```

## 支持的链接格式

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- YouTube播放列表链接

## 字幕烧录功能

本工具还提供了将VTT字幕文件烧录到视频中的功能，使用ffmpeg实现。

### 基本用法

```bash
# 基本烧录（自动生成输出文件名）
uv run subtitle_burner.py video.mp4 subtitles.vtt

# 指定输出文件
uv run subtitle_burner.py video.mp4 subtitles.vtt -o output_with_subs.mp4

# 自定义字体大小和颜色
uv run subtitle_burner.py video.mp4 subtitles.vtt --font-size 28 --font-color yellow

# 查看帮助
uv run subtitle_burner.py --help
```

### 字幕烧录参数

| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|---------|
| `video` | 输入视频文件路径 | - | - |
| `subtitle` | VTT字幕文件路径 | - | - |
| `-o, --output` | 输出视频文件路径 | - | 自动生成 |
| `--font-size` | 字体大小 | 数字 | 24 |
| `--font-color` | 字体颜色 | white, black, red, green, blue, yellow, cyan, magenta | white |

### 字幕烧录前提条件

使用字幕烧录功能需要安装ffmpeg：

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载并安装
```

### 完整工作流程示例

```bash
# 1. 下载YouTube视频和字幕
uv run youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" -q 1080p

# 2. 将字幕烧录到视频中
uv run subtitle_burner.py "Video Title.mp4" "Video Title.en.vtt" --font-size 26 --font-color yellow

# 输出: Video Title_with_subtitles.mp4

# 3. 智能分段视频（可选）
uv run video_segmenter.py "Video Title.mp4" "Video Title.en.vtt" -d 35

# 输出: segments/segment_001.mp4, segments/segment_002.mp4, ...
```

## 智能视频分段功能

视频分段工具可以基于VTT字幕内容智能地将长视频分割成多个短片段，每段30-40秒左右。

### 基本用法

```bash
# 基本分段（基于规则）
uv run video_segmenter.py "video.mp4" "subtitles.vtt"

# 自定义片段长度
uv run video_segmenter.py "video.mp4" "subtitles.vtt" -d 40

# 指定输出目录
uv run video_segmenter.py "video.mp4" "subtitles.vtt" -o my_segments

# 仅分析分段点（不生成视频）
uv run video_segmenter.py "video.mp4" "subtitles.vtt" --dry-run
```

### 使用LLM智能分段（可选）

```bash
# 使用OpenAI GPT进行智能分析
uv run video_segmenter.py "video.mp4" "subtitles.vtt" --api-key YOUR_OPENAI_API_KEY

# 使用不同的模型
uv run video_segmenter.py "video.mp4" "subtitles.vtt" --api-key YOUR_API_KEY --model gpt-4
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `video` | 输入视频文件路径 | - |
| `vtt` | VTT字幕文件路径 | - |
| `-d, --duration` | 目标片段时长（秒） | 35 |
| `-o, --output` | 输出目录 | segments |
| `--api-key` | LLM API密钥（可选） | - |
| `--model` | LLM模型名称 | gpt-3.5-turbo |
| `--dry-run` | 仅分析不生成视频 | - |

### 前提条件

- **ffmpeg**: 必须安装ffmpeg用于视频处理
- **VTT字幕文件**: 需要对应的字幕文件进行内容分析
- **LLM API密钥**: 使用智能分段功能需要（可选）

### 分段策略

1. **基于规则的分段**（默认）:
   - 在句子结束点分段（句号、问号、感叹号）
   - 在较长停顿处分段（超过1秒的间隔）
   - 确保每段时长在目标范围内

2. **LLM智能分段**（可选）:
   - 分析内容的逻辑结构
   - 在话题转换点分段
   - 保持内容的完整性和连贯性

## 免费LLM智能分段功能

免费LLM智能分段工具支持多种免费的AI模型进行更智能的视频分段，无需付费API即可享受AI分析。

### 基本用法

```bash
# 基于规则的智能分段（推荐，无需API）
uv run free-llm-segmenter "video.mp4" "subtitles.vtt"

# 使用Ollama本地模型（完全免费）
uv run free-llm-segmenter "video.mp4" "subtitles.vtt" --provider ollama

# 使用Hugging Face免费API
uv run free-llm-segmenter "video.mp4" "subtitles.vtt" --provider huggingface --api-key YOUR_HF_TOKEN
```

### 支持的免费LLM提供商

#### 1. Ollama本地模型（推荐）
```bash
# 安装Ollama
brew install ollama

# 启动服务
ollama serve

# 下载模型
ollama pull llama3.2

# 使用Ollama进行分段
uv run free-llm-segmenter "video.mp4" "subtitles.vtt" --provider ollama --model llama3.2
```

#### 2. Hugging Face Inference API
```bash
# 获取免费API Token: https://huggingface.co/settings/tokens
export HUGGINGFACE_API_KEY="your_token_here"

# 使用Hugging Face模型
uv run free-llm-segmenter "video.mp4" "subtitles.vtt" --provider huggingface
```

#### 3. 通义千问（阿里云）
```bash
# 获取API Key: https://dashscope.console.aliyun.com/
uv run free-llm-segmenter "video.mp4" "subtitles.vtt" --provider qwen --api-key YOUR_QWEN_KEY
```

#### 4. OpenAI（付费，但支持）
```bash
uv run free-llm-segmenter "video.mp4" "subtitles.vtt" --provider openai --api-key YOUR_OPENAI_KEY
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `video` | 输入视频文件路径 | - |
| `vtt` | VTT字幕文件路径 | - |
| `--provider` | LLM提供商 | rule |
| `--api-key` | API密钥 | - |
| `--model` | 模型名称 | 各提供商默认 |
| `--base-url` | API基础URL | 各提供商默认 |
| `-d, --duration` | 目标片段时长（秒） | 35 |
| `-o, --output` | 输出目录 | segments |
| `--dry-run` | 仅分析不生成视频 | - |

### 提供商对比

| 提供商 | 费用 | 安装难度 | 分析质量 | 推荐度 |
|--------|------|----------|----------|--------|
| rule | 免费 | 无需安装 | 良好 | ⭐⭐⭐⭐ |
| ollama | 免费 | 中等 | 优秀 | ⭐⭐⭐⭐⭐ |
| huggingface | 免费 | 简单 | 良好 | ⭐⭐⭐⭐ |
| qwen | 有限免费 | 简单 | 优秀 | ⭐⭐⭐ |
| openai | 付费 | 简单 | 优秀 | ⭐⭐ |

### 技术特点

- **多提供商支持**: 支持5种不同的LLM提供商
- **智能回退**: 如果LLM分析失败，自动回退到基于规则的方法
- **本地优先**: 推荐使用Ollama本地模型，保护隐私且完全免费
- **灵活配置**: 支持自定义模型、API地址等参数
- **干运行模式**: 可以先分析分段点，确认后再实际分割

## VTT到SRT字幕格式转换

本工具提供了将VTT字幕文件转换为SRT格式的功能，支持单文件转换和批量转换。

### 基本用法

```bash
# 转换单个VTT文件
uv run vtt-to-srt "subtitle.vtt"

# 转换指定的VTT文件
uv run vtt_to_srt_converter.py "subtitle.vtt"

# 批量转换当前目录下所有VTT文件
uv run vtt_to_srt_converter.py --batch

# 查看帮助
uv run vtt-to-srt --help
```

### 转换示例

```bash
# 转换YouTube下载的字幕文件
uv run vtt-to-srt "Video Title.en.vtt"
# 输出: Video Title.en.srt

# 转换带特殊字符的文件名
uv run vtt-to-srt "Rate Limiter System Design #techprep.en.vtt"
# 输出: Rate Limiter System Design #techprep.en.srt
```

### 功能特点

- **精确转换**: 保持时间戳的精确性，支持毫秒级转换
- **格式清理**: 自动清理VTT特有的标记和格式
- **批量处理**: 支持一次性转换多个文件
- **智能命名**: 自动生成对应的SRT文件名
- **错误处理**: 完善的错误处理和用户提示

### 转换对比

**VTT格式示例:**
```
WEBVTT

00:00:00.040 --> 00:00:01.510
let's understand how to design a rate

00:00:01.520 --> 00:00:03.869
limiter in under 60 seconds
```

**转换后的SRT格式:**
```
1
00:00:00,040 --> 00:00:01,510
let's understand how to design a rate

2
00:00:01,520 --> 00:00:03,869
limiter in under 60 seconds
```

### 技术特点

- 🔄 **格式标准化**: 严格按照SRT格式标准进行转换
- ⚡ **高效处理**: 快速解析和转换大型字幕文件
- 🎯 **精确时间**: 保持毫秒级时间戳精度
- 📝 **文本清理**: 自动处理VTT特有标记
- 🛡️ **错误恢复**: 跳过损坏的条目，继续处理其他内容

### 免费LLM替代方案

如果不想使用付费的OpenAI API，可以考虑以下免费替代方案：

- **Hugging Face Inference API**: 免费额度的开源模型
- **Ollama**: 本地运行开源模型
- **Google Colab**: 免费GPU运行本地模型
- **国产模型**: 通义千问、文心一言等提供免费API

### 技术特点

- 🎯 **智能断点检测**: 基于内容语义和自然停顿
- ⚡ **高效处理**: 使用ffmpeg的copy模式，无需重新编码
- 🔧 **灵活配置**: 支持自定义片段长度和输出目录
- 📊 **详细分析**: 提供分段信息和时长统计
- 🤖 **AI增强**: 可选的LLM智能分析

## 下载设置

- **视频质量**: 优先下载720p，如果不可用则下载最佳质量
- **字幕**: 自动下载英文和中文字幕（如果可用）
- **文件名**: 使用视频标题作为文件名
- **Cookie支持**: 默认从Chrome导入cookies，可选择其他浏览器或禁用
- **重试机制**: 自动重试失败的下载和片段

## 命令行参数

### 基本参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `url` | YouTube视频或播放列表链接 | `"https://www.youtube.com/watch?v=VIDEO_ID"` |
| `-o, --output` | 输出目录路径 | `-o "/path/to/output"` |

### 视频质量和格式
| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|--------|
| `-q, --quality` | 视频质量 | `720p`, `1080p`, `best`, `worst` | `720p` |

### 音频选项
| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|--------|
| `--audio-only` | 只下载音频（最佳音频质量） | - | - |
| `--extract-audio` | 下载视频并提取音频文件 | - | - |
| `--audio-format` | 音频格式 | `mp3`, `aac`, `flac`, `wav` | `mp3` |

### 播放列表选项
| 参数 | 说明 |
|------|------|
| `--playlist` | 下载整个播放列表 |

### 信息查询选项
| 参数 | 说明 |
|------|------|
| `--list-formats` | 列出可用的视频格式而不下载 |
| `--get-title` | 获取视频标题而不下载 |
| `--get-description` | 获取视频描述而不下载 |

### Cookie和浏览器设置
| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|--------|
| `--browser` | 选择浏览器导入cookies | `chrome`, `firefox`, `safari`, `edge` | `chrome` |
| `--no-cookies` | 禁用cookie导入 | - | - |

## 注意事项

1. **Cookie支持**：如果遇到"Sign in to confirm you're not a bot"错误，请使用`--browser`参数指定浏览器导入cookies，或使用`--no-cookies`禁用cookie功能
2. **视频质量**：`best`和`worst`会自动选择最佳/最差可用质量，具体数值（如`720p`、`1080p`）会尝试下载指定质量
3. **音频格式**：使用`--extract-audio`时会同时保存视频和音频文件，使用`--audio-only`只保存音频文件
4. **播放列表**：下载播放列表时会在输出目录创建以播放列表名称命名的子文件夹
5. **信息查询**：使用信息查询选项（如`--get-title`）时不会下载任何文件，只显示信息
6. 首次运行时会自动安装`yt-dlp`依赖
7. 视频将保存到指定的输出目录或当前文件夹
8. 支持下载英文和中文字幕
9. 如果使用`uv`，建议使用`uv run`命令以获得最佳体验
10. **基于yt-dlp**：本项目基于yt-dlp库，相比原始youtube-dl具有更好的稳定性和更频繁的更新
11. **字幕烧录**：使用字幕烧录功能需要先安装ffmpeg，烧录过程会重新编码视频，可能需要较长时间
12. **视频分段**：使用视频分段功能需要先安装ffmpeg，分段过程使用copy模式，速度较快但仍需要一定时间
13. **免费LLM分段**：推荐使用Ollama本地模型进行智能分段，完全免费且保护隐私；其他提供商可能需要API密钥
14. 请确保网络连接稳定
15. 某些视频可能因版权限制无法下载
16. 下载速度取决于网络状况和视频大小
17. 请遵守YouTube的使用条款和版权法律

## 故障排除

如果遇到问题，请尝试：

1. 更新yt-dlp:
   - 使用uv: `uv add yt-dlp@latest`
   - 使用pip: `pip install --upgrade yt-dlp`
2. 检查网络连接
3. 确认视频链接有效
4. 检查是否有足够的磁盘空间
5. 确保uv已正确安装: `uv --version`

## 依赖库

- [yt-dlp](https://github.com/yt-dlp/yt-dlp): YouTube视频下载库
- [uv](https://github.com/astral-sh/uv): 现代Python包管理器（推荐）

## 关于uv

uv是一个极快的Python包管理器，用Rust编写。相比pip，它具有以下优势：
- 🚀 更快的依赖解析和安装
- 🔒 更好的依赖锁定
- 📦 内置虚拟环境管理
- 🛠️ 更现代的项目管理工具

如果您还没有安装uv，可以通过以下方式安装：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
uv run python youtube_downloader.py --browser chrome -q 1080p --convert-vtt-to-text https://www.youtube.com/shorts/xMlsVPH_SWA
# English_Shorts_Learning
