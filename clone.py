#!/usr/bin/env python3
"""
MiMo V2.5 TTS Voice Clone — 通用语音克隆工具

用法：
    python clone.py --audio 你的声音.wav --text "要合成的文案" --api-key YOUR_KEY
    python clone.py --audio 你的声音.wav --text-file 文案.txt --api-key YOUR_KEY

环境变量：
    MIMO_API_KEY — 也可以不传 --api-key，从环境变量读取
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests
import soundfile as sf

ENDPOINT = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
DEFAULT_STYLE = (
    "语速适中，断句干脆。每句话之间有明显气口，但不拖。"
    "像短视频口播一样干脆利落，有顿挫感。"
)


def b64_file(path: str) -> str:
    """读取文件并返回 Base64 编码"""
    raw = Path(path).read_bytes()
    encoded = base64.b64encode(raw).decode("utf-8")
    if len(encoded) > 10_485_760:
        print("❌ 音频 Base64 超过 10MB，请裁剪音频。")
        sys.exit(1)
    return encoded


def detect_mime(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in (".mp3",):
        return "audio/mpeg"
    return "audio/wav"


def loudnorm(input_wav: str, output_wav: str) -> None:
    subprocess.run(
        [
            "ffmpeg", "-i", input_wav, "-af",
            "loudnorm=I=-14:LRA=11:TP=-1.5",
            "-ar", "24000", output_wav, "-y",
        ],
        capture_output=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="MiMo V2.5 TTS 语音克隆 — 用你的声音合成任意文案"
    )
    parser.add_argument(
        "--audio", required=True,
        help="参考音频路径 (WAV 或 MP3，15-60 秒单声道效果最佳)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="直接输入文案")
    group.add_argument("--text-file", help="从 .txt 文件读取文案")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("MIMO_API_KEY", ""),
        help="MiMo API Key（或设置 MIMO_API_KEY 环境变量）",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="输出 WAV 路径（默认：克隆文案前缀_时间戳.wav）",
    )
    parser.add_argument(
        "--style",
        default=DEFAULT_STYLE,
        help="风格指令（自然语言描述语速、语气、情绪等）",
    )
    parser.add_argument(
        "--no-loudnorm", action="store_true",
        help="跳过响度归一化",
    )
    args = parser.parse_args()

    # --- 校验 ---
    if not args.api_key:
        print("❌ 未提供 API Key。请用 --api-key 传入，或设置环境变量 MIMO_API_KEY。")
        print("   获取 Key：https://platform.xiaomimimo.com → 控制台 → API Key")
        sys.exit(1)

    if not Path(args.audio).exists():
        print(f"❌ 音频文件不存在：{args.audio}")
        sys.exit(1)

    # --- 文案 ---
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    else:
        text = args.text
    text = text.strip()
    if not text:
        print("❌ 文案为空。")
        sys.exit(1)

    # --- 输出路径 ---
    if args.output is None:
        prefix = re.sub(r'[，。！？、\s\n：""——]', '', text)[:12]
        ts = datetime.now().strftime("%m%d_%H%M%S")
        args.output = f"clone_{prefix}_{ts}.wav"

    # --- 合成 ---
    mime = detect_mime(args.audio)
    voice_b64 = b64_file(args.audio)
    print(f"🎤 参考音频：{Path(args.audio).name}（{mime}，Base64 {len(voice_b64)//1024} KB）")
    print(f"📝 文案字数：{len(text)}")
    print("⏳ 调用 MiMo API...")

    resp = requests.post(
        ENDPOINT,
        json={
            "model": "mimo-v2.5-tts-voiceclone",
            "messages": [
                {"role": "user", "content": args.style},
                {"role": "assistant", "content": text},
            ],
            "audio": {
                "format": "wav",
                "voice": f"data:{mime};base64,{voice_b64}",
            },
        },
        headers={
            "Content-Type": "application/json",
            "api-key": args.api_key,
        },
        timeout=300,
    )

    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}: {resp.text[:400]}")
        sys.exit(1)

    data = resp.json()
    audio_b64 = data["choices"][0]["message"]["audio"]["data"]
    raw_bytes = base64.b64decode(audio_b64)

    if args.no_loudnorm:
        Path(args.output).write_bytes(raw_bytes)
        d, sr = sf.read(args.output)
    else:
        tmp = args.output.replace(".wav", "_tmp.wav")
        Path(tmp).write_bytes(raw_bytes)
        loudnorm(tmp, args.output)
        os.remove(tmp)
        d, sr = sf.read(args.output)

    print(f"✅ 完成！{len(d)/sr:.1f}s · {sr}Hz · {args.output}")


if __name__ == "__main__":
    main()
