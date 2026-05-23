# MiMo Voice Cloner 🎤

用 MiMo V2.5 TTS API 克隆任意人声，将文案合成为自然语音。

**一条命令，三样东西：你的音频 + MiMo Key + 文案 → 克隆声音的语音文件。**

## 快速开始

### 1. 注册 MiMo

去 [platform.xiaomimimo.com](https://platform.xiaomimimo.com) 注册 → 控制台 → 生成 API Key。当前 **限时免费**。

### 2. 安装依赖

```bash
pip install requests soundfile
```

需要 `ffmpeg`（用于响度归一化），无 ffmpeg 可加 `--no-loudnorm` 跳过。Windows 用户可 `winget install ffmpeg`。

### 3. 克隆你的第一段语音

```bash
python clone.py --audio 你的声音.wav --text "你好，这是我的克隆声音。" --api-key 你的key
```

## 用法

```bash
# 直接输入文案
python clone.py --audio voice.wav --text "要合成的文字" --api-key YOUR_KEY

# 从文件读取文案
python clone.py --audio voice.wav --text-file 文案.txt --api-key YOUR_KEY

# 自定义风格
python clone.py --audio voice.wav --text "文案" \
  --style "语速缓慢，深沉有力，像纪录片旁白。"

# 指定输出路径
python clone.py --audio voice.wav --text "文案" -o output.wav

# 跳过响度归一化（无 ffmpeg 时）
python clone.py --audio voice.wav --text "文案" --no-loudnorm
```

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--audio` | ✅ | 参考音频路径，WAV 或 MP3，15-60 秒最佳 |
| `--text` | ✅ | 要合成的文案（与 --text-file 二选一） |
| `--text-file` | ✅ | 从 .txt 读取文案 |
| `--api-key` | ✅ | MiMo API Key，也可设环境变量 `MIMO_API_KEY` |
| `--output` | 否 | 输出路径，默认 `clone_文案前缀_时间戳.wav` |
| `--style` | 否 | 风格指令（自然语言描述语气/语速/情绪） |
| `--no-loudnorm` | 否 | 跳过响度归一化 |

### 默认风格

```
语速适中，断句干脆。每句话之间有明显气口，但不拖。
像短视频口播一样干脆利落，有顿挫感。
```

## 参考音频要求

- **格式**：WAV 或 MP3
- **时长**：15-60 秒，长一点克隆更准
- **内容**：单人纯人声，无背景音乐或噪音
- **大小**：Base64 编码后不超过 10 MB

## 输出

- 格式：24000 Hz 单声道 WAV
- 自动响度归一化（-14 LUFS，适合短视频平台）
- 文件名自动包含文案前缀 + 时间戳，方便区分

## 工作原理

1. 将参考音频 Base64 编码后发送给 MiMo API
2. MiMo V2.5-TTS-VoiceClone 模型根据参考音频克隆音色
3. 用克隆音色朗读目标文案
4. 返回 WAV 音频，经 ffmpeg 响度归一化后输出

## 常见问题

**Q: API Key 从哪来？**  
A: [platform.xiaomimimo.com](https://platform.xiaomimimo.com) 注册后控制台生成。目前免费。

**Q: 为什么声音很小？**  
A: 确保安装了 ffmpeg，脚本会自动做响度归一化。否则加 `--no-loudnorm` 跳过。

**Q: 长文案能合成吗？**  
A: 单次 500 字以内没问题，再长建议分段。

**Q: 克隆效果不好怎么办？**  
A: 换一段更清晰、更长的参考音频（30-60 秒），确保是单人纯人声。

## License

MIT

## Author

微博 [@科技锐评](https://www.weibo.com/u/3315426953)
