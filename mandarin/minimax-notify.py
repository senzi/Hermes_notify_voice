#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
minimax-notify —— 本地语音播报 CLI（MiniMax TTS）

用法:
  minimax-notify.py "任务出现状况，请到会话中查看"
  minimax-notify.py -s alert "任务出错，请查看"
  minimax-notify.py -v yujie "进度更新了"
  minimax-notify.py --no-play -o out.wav "只合成不播放"
  minimax-notify.py --voices

API key: 同目录 key.txt（或环境变量 MINIMAX_API_KEY）
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

try:
    import winsound
except ImportError:  # 非 Windows 环境降级
    winsound = None

API_ENDPOINTS = [
    "https://api.minimaxi.com/v1/t2a_v2",
    "https://api-bj.minimaxi.com/v1/t2a_v2",
]

DEFAULT_MODEL = "speech-2.8-turbo"

# 预置音色别名 -> MiniMax voice_id（完整列表见平台文档 /docs/faq/system-voice-id）
VOICES = {
    "news_anchor": "Chinese (Mandarin)_News_Anchor",
    "announcer": "Chinese (Mandarin)_Male_Announcer",
    "yujie": "female-yujie",
    "tianmei": "female-tianmei",
    "robot": "Robot_Armor",
    "bestie": "Chinese (Mandarin)_Warm_Bestie",
    "qingse": "male-qn-qingse",
    "jingying": "male-qn-jingying",
    # 粤语（白话）—— 本账号可用的全部 6 个
    "yue_kind": "Cantonese_KindWoman",
    "yue_gentle": "Cantonese_GentleLady",
    "yue_cute": "Cantonese_CuteGirl",
    "yue_playful": "Cantonese_PlayfulMan",
    "yue_host_f": "Cantonese_ProfessionalHost（F)",
    "yue_host_m": "Cantonese_ProfessionalHost（M)",
}

# 提示音预设：(频率Hz, 时长ms) 序列；None 表示 80ms 停顿
SOUNDS = {
    "ding":   [(1200, 150)],
    "double": [(1200, 120), None, (1200, 120)],
    "alert":  [(880, 200), (1320, 200), (880, 200)],
    "chime":  [(660, 120), (880, 120), (1100, 180)],
    "none":   [],
}


def load_config():
    """读取同目录 config.json；缺失或损坏时返回空 dict（用代码默认值）。"""
    cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(cfg_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg if isinstance(cfg, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def load_api_key():
    env = os.environ.get("MINIMAX_API_KEY")
    if env and env.strip():
        return env.strip()
    key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "key.txt")
    if os.path.isfile(key_file):
        with open(key_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    sys.exit("错误: 未找到 API key。请在 key.txt 写入 MiniMax 接口密钥（# 开头为注释），或设置环境变量 MINIMAX_API_KEY。")


def play_sound(name):
    """本地合成提示音（winsound.Beep，零成本零延迟）。"""
    if winsound is None or name == "none":
        return
    for item in SOUNDS.get(name, SOUNDS["ding"]):
        if item is None:
            time.sleep(0.08)
        else:
            freq, ms = item
            winsound.Beep(freq, ms)


def synthesize(text, voice_id, model, vol, speed, lang=""):
    """调用 MiniMax 同步 TTS，返回 wav 音频字节。主地址失败自动试备用地址。

    ``lang`` 是 language_boost：粤语必须传 "Chinese,Yue"，否则按普通读音念；留空则不传该字段。
    """
    payload = {
        "model": model,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": vol,
            "pitch": 0,
        },
        "audio_setting": {
            "format": "wav",
            "sample_rate": 32000,
            "channel": 1,
        },
        "output_format": "hex",
    }
    if lang:  # 语言增强：粤语需 "Chinese,Yue"（只认 Chinese / Chinese,Yue / auto）
        payload["language_boost"] = lang
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {load_api_key()}",
        "Content-Type": "application/json",
    }

    last_err = None
    for url in API_ENDPOINTS:
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
            return parse_response(body)
        except Exception as e:  # noqa: BLE001 —— 逐地址重试，最终统一报错
            last_err = e
    raise RuntimeError(f"TTS 请求失败: {last_err}")


def parse_response(body):
    obj = json.loads(body)
    base = obj.get("base_resp") or {}
    if base.get("status_code") != 0:
        raise RuntimeError(f"接口错误 {base.get('status_code')}: {base.get('status_msg')}")
    data = obj.get("data") or {}
    audio_hex = data.get("audio")
    if not audio_hex:
        raise RuntimeError("接口返回无音频数据")
    audio = bytes.fromhex(audio_hex)
    info = obj.get("extra_info") or {}
    return audio, obj.get("trace_id", ""), info


def play_wav(audio):
    """写临时 wav 文件并阻塞播放（SND_FILENAME 无内存上限问题）。"""
    if winsound is None:
        raise RuntimeError("当前环境不支持 winsound（非 Windows？）")
    fd, path = tempfile.mkstemp(suffix=".wav", prefix="minimax_notify_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(audio)
        winsound.PlaySound(path, winsound.SND_FILENAME)  # 阻塞直到播完
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def play_wav_async(audio):
    """异步播放：spawn 独立子进程播放，主进程立即返回（调用侧不阻塞）。"""
    if winsound is None:
        raise RuntimeError("当前环境不支持 winsound（非 Windows？）")
    fd, path = tempfile.mkstemp(suffix=".wav", prefix="minimax_notify_")
    with os.fdopen(fd, "wb") as f:
        f.write(audio)
    code = ("import winsound,sys,os;"
            "winsound.PlaySound(sys.argv[1], winsound.SND_FILENAME);"
            "os.unlink(sys.argv[1])")
    # CREATE_NO_WINDOW：不弹 cmd/conhost 窗口（注意别用 DETACHED_PROCESS，会闪窗）
    # CREATE_NEW_PROCESS_GROUP：脱离调用进程组独立存活（防父进程组被整组收走→静音）
    # 重定向 std 到 DEVNULL：子进程不引用父进程句柄
    subprocess.Popen([sys.executable, "-c", code, path],
                     creationflags=0x08000000 | 0x00000200,  # CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     close_fds=True)


def estimate_cost(text):
    """按 speech-2.8-turbo 2元/万字符估算：汉字算 2 字符，其余算 1 字符。"""
    chars = 0
    for ch in text:
        chars += 2 if ord(ch) > 0x2E7F else 1
    return chars / 10000 * 2.0


def main():
    cfg = load_config()
    parser = argparse.ArgumentParser(
        prog="minimax-notify",
        description="本地语音播报：MiniMax TTS 合成 + 提示音播放（默认值来自 config.json，命令行参数优先）",
    )
    parser.add_argument("text", nargs="?", help="播报文本")
    parser.add_argument("-s", "--sound", choices=list(SOUNDS.keys()), default=cfg.get("sound", "ding"),
                        help="提示音（默认 ding）")
    parser.add_argument("-v", "--voice", default=cfg.get("voice", "news_anchor"),
                        help="音色 ID 或预置别名（--voices 查看）")
    parser.add_argument("-m", "--model", default=cfg.get("model", DEFAULT_MODEL), help="TTS 模型（默认 speech-2.8-turbo）")
    parser.add_argument("--vol", type=float, default=cfg.get("vol", 1.0), help="音量（0-10，默认取 config.json，官方默认 1.0）")
    parser.add_argument("--speed", type=float, default=cfg.get("speed", 1.0), help="语速（默认 1.0）")
    parser.add_argument("-o", "--out", help="保存音频到指定路径（仍会播放，除非 --no-play）")
    parser.add_argument("--no-play", action="store_true", help="只合成不播放")
    parser.add_argument("--async", dest="async_play", action="store_true",
                        help="异步播放：立即返回，子进程播放（默认同步，播完才返回，保证出声）")
    parser.add_argument("--lang", default=cfg.get("language_boost", ""),
                        help="语言增强：Chinese / Chinese,Yue / auto（默认取 config.json 的 language_boost，留空不传）")
    parser.add_argument("--voices", action="store_true", help="列出预置音色与提示音后退出")
    args = parser.parse_args()

    if args.voices:
        print("预置音色（--voice 可直接传任意 MiniMax voice_id）:")
        for alias, vid in VOICES.items():
            print(f"  {alias:<12} {vid}")
        print("\n提示音（--sound）:")
        for name in SOUNDS:
            print(f"  {name}")
        return

    if not args.text:
        parser.error("缺少播报文本")

    voice_id = VOICES.get(args.voice, args.voice)

    # 1. 提示音
    play_sound(args.sound)

    # 2. 合成
    t0 = time.time()
    try:
        audio, trace_id, info = synthesize(args.text, voice_id, args.model, args.vol, args.speed, args.lang)
    except Exception as e:  # noqa: BLE001 —— TTS 失败降级：提示音已在步骤1播过，至少留个响，干净报错
        print(f"⚠️ 合成失败，仅播了提示音（无语音，请到会话查看）: {e}", file=sys.stderr)
        sys.exit(2)
    elapsed = time.time() - t0

    # 3. 保存/播放
    if args.out:
        with open(args.out, "wb") as f:
            f.write(audio)
        print(f"已保存: {args.out} ({len(audio)} bytes)")
    if not args.no_play:
        try:
            if args.async_play:
                play_wav_async(audio)  # 显式 --async：立即返回，子进程播放
            else:
                play_wav(audio)  # 默认同步：播完才返回，保证出声
        except Exception as e:  # noqa: BLE001 —— 播放失败不吞掉，但已合成成功
            print(f"警告: 播放失败: {e}", file=sys.stderr)
            sys.exit(2)

    # 4. 汇报
    cost = estimate_cost(args.text)
    mode = "async" if args.async_play else "sync"
    print(f"[ok:{mode}] {args.text!r} | {voice_id} | {args.model} | 合成 {elapsed:.1f}s | "
          f"音频 {info.get('audio_length', '?')}ms / {len(audio)} bytes | 约 {cost:.4f} 元 | trace {trace_id}")


if __name__ == "__main__":
    main()
