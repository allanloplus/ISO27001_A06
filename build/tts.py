# -*- coding: utf-8 -*-
"""產生每句旁白語音、合成整段 narration.mp3，並輸出時間軸 timeline.js 與講稿。

用法：python3 build/tts.py
需求：pip install edge-tts；系統需有 ffmpeg / ffprobe。
"""
import array
import asyncio
import json
import os
import ssl
import subprocess
import sys
import wave
from pathlib import Path

import edge_tts
import edge_tts.communicate as _cm

sys.path.insert(0, str(Path(__file__).parent))
from script import SCENES, VOICES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LINES_DIR = ROOT / "build" / "lines"
SLIDES = ROOT / "slides"
SR = 24000

GAP = 0.35          # 句與句之間
SCENE_LEAD = 0.9    # 換場後先讓畫面進場
SCENE_TAIL = 0.9    # 每場結尾停頓

# 走代理時改用代理的 CA bundle
_ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if Path("/root/.ccr/ca-bundle.crt").exists() else None)
if _ca:
    _cm._SSL_CTX = ssl.create_default_context(cafile=_ca)
PROXY = os.environ.get("HTTPS_PROXY")


async def synth(text, spk, out):
    if out.exists() and out.stat().st_size > 0:
        return
    v = VOICES[spk]
    for attempt in range(4):
        try:
            c = edge_tts.Communicate(text, v["voice"], rate=v["rate"], pitch=v["pitch"], proxy=PROXY)
            await c.save(str(out))
            return
        except Exception as e:  # 網路偶發錯誤重試
            print("retry", out.name, e)
            await asyncio.sleep(2 ** attempt)
    raise RuntimeError(f"TTS failed: {out}")


def decode(mp3):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    a = array.array("h")
    a.frombytes(raw)
    return a


async def main():
    LINES_DIR.mkdir(parents=True, exist_ok=True)
    jobs = []
    for s in SCENES:
        for i, (spk, text) in enumerate(s["lines"]):
            jobs.append(synth(text, spk, LINES_DIR / f"{s['id']}_{i:02d}.mp3"))
    # 控制併發數量
    for k in range(0, len(jobs), 6):
        await asyncio.gather(*jobs[k:k + 6])

    track = array.array("h")
    t = 0.0
    timeline = {"scenes": [], "lines": []}

    def pad_to(sec):
        n = int(round(sec * SR)) - len(track)
        if n > 0:
            track.extend([0] * n)

    for si, s in enumerate(SCENES):
        scene = {"id": s["id"], "section": s["section"], "title": s["title"], "start": round(t, 3), "lines": []}
        t += SCENE_LEAD
        for i, (spk, text) in enumerate(s["lines"]):
            pcm = decode(LINES_DIR / f"{s['id']}_{i:02d}.mp3")
            dur = len(pcm) / SR
            pad_to(t)
            track.extend(pcm)
            scene["lines"].append(len(timeline["lines"]))
            timeline["lines"].append({"scene": si, "i": i, "spk": spk, "text": text,
                                      "start": round(t, 3), "dur": round(dur, 3)})
            t += dur + GAP
        t += SCENE_TAIL - GAP
        scene["end"] = round(t, 3)
        timeline["scenes"].append(scene)
    pad_to(t + 0.5)
    timeline["duration"] = round(t, 3)

    wav = ROOT / "build" / "narration.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(track.tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5",
                    "-ar", "44100", "-b:a", "96k", str(SLIDES / "narration.mp3")], check=True)

    (SLIDES / "timeline.js").write_text(
        "// 由 build/tts.py 自動產生，請勿手動修改\nwindow.TIMELINE = "
        + json.dumps(timeline, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")

    # 講稿
    name = {"A": "Allan老師", "R": "助教阿拉蕾"}
    md = ["# ISO 27001:2022 A.8.9 組態管理 — 動畫簡報講稿", "",
          f"總長度約 {int(t // 60)} 分 {int(t % 60)} 秒。", ""]
    for s in timeline["scenes"]:
        mm, ss = divmod(int(s["start"]), 60)
        md += [f"## {mm:02d}:{ss:02d}　{s['section']}｜{s['title']}", ""]
        for li in s["lines"]:
            L = timeline["lines"][li]
            md.append(f"- **{name[L['spk']]}**：{L['text']}")
        md.append("")
    (ROOT / "docs" / "講稿.md").write_text("\n".join(md), encoding="utf-8")
    print(f"done: {len(timeline['lines'])} lines, {t:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
