#!/usr/bin/env python3
"""Kokoro-on-a-Mac narration: one WAV per section, with the delivery that sounded most human by ear.

    python voice.py      # needs: pip install kokoro soundfile numpy   -> ./out/voices/sNN.wav + timing.json

Delivery rules: one sentence per Kokoro call with its ~0.9 s padding
trimmed; "…" becomes a real beat; {H} punchlines slower with a beat before and a hold after; long
asides a bit faster. {H}/{U} tags are stripped.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("OUT_DIR", HERE / "out"))
SR = 24000
VOICE = "am_puck"
SPEED = {"base": 0.92, "punch": 0.86, "human": 0.95, "long": 0.97}
PAUSE = {"sentence": 0.3, "before_punch": 0.45, "after_punch": 0.55, "beat": 0.6, "section": 0.8}
SPOKEN = {"M1": "M one", "GPU": "G P U"}
# per-section trim to land each section in 173-200 wpm (measured, then re-voiced; see CHECKPLAN G2)
SECTION_TRIM = {1: 1.12, 3: 1.03, 4: 1.03, 7: 0.9}


def sections(md: str) -> list[tuple[str, list[str]]]:
    body = md
    out, name = [], None
    for line in body.splitlines():
        if line.startswith("## "):
            name = line[3:].strip(); out.append((name, []))
        elif line.startswith(">") and out:
            out[-1][1].append(line[1:].strip())
    return [(n, s) for n, s in out if s]


def trim(a: np.ndarray, thr: float = 0.01, keep: float = 0.04) -> np.ndarray:
    idx = np.where(np.abs(a) > thr)[0]
    if not len(idx):
        raise ValueError("silent render")
    k = int(SR * keep)
    return a[max(0, idx[0] - k): idx[-1] + k]


def main() -> None:
    pipe = KPipeline(lang_code="a")
    out = ROOT / "voices"; out.mkdir(parents=True, exist_ok=True)
    timing = []
    for i, (name, lines) in enumerate(sections((HERE / "narration.md").read_text()), 1):
        sents = [s for l in lines for s in re.split(r"(?<=[.?!])\s+(?=\{|[A-Z\"'])", l) if s.strip()]
        parts, words, sent_t = [], 0, []
        for j, s in enumerate(sents):
            kind = "punch" if s.startswith("{H}") else "human" if s.startswith("{U}") else "long" if len(s.split()) > 22 else "base"
            text = re.sub(r"\{[HU]\}", "", s).strip()
            for k, v in SPOKEN.items():
                text = re.sub(rf"\b{re.escape(k)}\b", v, text)
            words += len(text.split())
            if kind == "punch" and parts:
                parts.append(np.zeros(int(SR * (PAUSE["before_punch"] - PAUSE["sentence"]))))
            t0 = sum(len(x) for x in parts) / SR
            pieces = [p for p in re.split(r"\s*…\s*", text) if p]
            for n, piece in enumerate(pieces):
                parts.append(trim(np.concatenate([r.audio for r in pipe(piece, voice=VOICE, speed=SPEED[kind] * SECTION_TRIM.get(i, 1.0))])))
                if n < len(pieces) - 1:
                    parts.append(np.zeros(int(SR * PAUSE["beat"])))
            sent_t.append({"text": text, "kind": kind, "start": round(t0, 2), "end": round(sum(len(x) for x in parts) / SR, 2)})
            parts.append(np.zeros(int(SR * (PAUSE["after_punch"] if kind == "punch" else PAUSE["sentence"]))))
        parts.append(np.zeros(int(SR * PAUSE["section"])))
        audio = np.concatenate(parts)
        sf.write(out / f"s{i:02d}.wav", audio / max(1e-9, np.abs(audio).max()) * 0.85, SR)
        dur = len(audio) / SR
        timing.append({"id": i, "section": name, "words": words, "seconds": round(dur, 2), "wpm": round(words / (dur / 60), 1), "sentences": sent_t})
        print(f"s{i:02d} {dur:6.1f}s {words:4d} words {timing[-1]['wpm']:6.1f} wpm  {name}")
    total = sum(t["seconds"] for t in timing)
    (out / "timing.json").write_text(json.dumps({"voice": VOICE, "speed": SPEED, "pause": PAUSE, "sections": timing}, indent=1) + "\n")
    print(f"total {total/60:.2f} min, {sum(t['words'] for t in timing)} words, {sum(t['words'] for t in timing)/(total/60):.0f} wpm")


if __name__ == "__main__":
    main()
