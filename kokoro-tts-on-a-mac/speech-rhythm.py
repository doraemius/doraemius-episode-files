#!/usr/bin/env python3
"""Measure how a narrator varies pace and pauses: human vs TTS, on the same instrument.

Word timestamps from faster-whisper (medium, int8, CPU) -> the gaps between words are pauses;
a gap >= --phrase-gap splits phrases; each phrase of >= 4 words gets its own words-per-minute.

Reported per file:
  wpm_overall        words / (last word end - first word start) * 60, pauses included
  articulation_wpm   words / time actually spent inside words: pace with the pauses removed
  phrase_wpm p10/p50/p90 and CV   spread of pace between phrases (CV = stdev / mean)
  pauses/min, pause p50/p90       gaps >= --pause-gap between words
  long pauses/min                 gaps >= 0.6 s: the "let it land" pauses of public speaking
  --pitch adds, per phrase of >= 4 words and >= 1 s (the SAME word-gap phrases, so audience noise
  cannot move the boundaries): melody_sameness = mean pairwise correlation of each phrase's pitch
  curve (pyin, semitones re the phrase median, 20 points), end_fall = mean last-minus-first semitones,
  phrase_pitch_range_p50 = median p5-p95 semitone range inside a phrase.

    python speech-rhythm.py a.wav b.webm --seconds 180 --json out.json

The input window is the first --seconds of each file (ffmpeg decodes anything). Thresholds are
pre-set, not tuned on the files: pause 0.15 s (below that is articulation, not a pause), phrase 0.25 s.
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Rhythm:
    file: str
    words: int
    seconds: float
    wpm_overall: float
    articulation_wpm: float
    phrases: int
    phrase_wpm_p10: float
    phrase_wpm_p50: float
    phrase_wpm_p90: float
    phrase_wpm_cv: float
    pauses_per_min: float
    pause_p50_s: float
    pause_p90_s: float
    long_pauses_per_min: float
    melody_sameness: float | None = None
    end_fall_st: float | None = None
    phrase_pitch_range_p50: float | None = None


def pct(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * (len(xs) - 1) + 0.5))] if xs else 0.0


def decode(path: Path, seconds: int, out: Path) -> None:
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(path), "-t", str(seconds),
                    "-ac", "1", "-ar", "16000", str(out)], check=True)


def melody(wav: Path, phrases: list) -> tuple[float, float, float] | None:
    import itertools
    import librosa
    import numpy as np
    y, sr = librosa.load(str(wav), sr=16000)
    f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=400, sr=sr, frame_length=1024, hop_length=160)
    curves, ranges, falls = [], [], []
    for p in phrases:
        if len(p) < 4 or p[-1].end - p[0].start < 1.0:
            continue
        seg = f0[int(p[0].start * 100): int(p[-1].end * 100)]
        seg = seg[~np.isnan(seg)]
        if len(seg) < 25:
            continue
        stn = 12 * np.log2(seg / np.median(seg))
        c = np.interp(np.linspace(0, 1, 20), np.linspace(0, 1, len(stn)), stn)
        curves.append(c); falls.append(c[-4:].mean() - c[:4].mean())
        ranges.append(np.percentile(stn, 95) - np.percentile(stn, 5))
    if len(curves) < 5:
        return None
    r = [np.corrcoef(curves[i], curves[j])[0, 1] for i, j in itertools.combinations(range(len(curves)), 2)]
    return round(float(np.mean(r)), 3), round(float(np.mean(falls)), 2), round(float(np.median(ranges)), 2)


def measure(path: Path, model, seconds: int, pause_gap: float, phrase_gap: float, pitch: bool = False) -> Rhythm:
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "a.wav"
        decode(path, seconds, wav)
        segs, _ = model.transcribe(str(wav), language="en", word_timestamps=True, vad_filter=False,
                                   beam_size=1, condition_on_previous_text=False)
        words = [w for s in segs for w in (s.words or [])]
        if pitch and len(words) >= 30:
            gaps0 = [b.start - a.end for a, b in zip(words, words[1:])]
            ph, cur = [], [words[0]]
            for g, w in zip(gaps0, words[1:]):
                if g >= phrase_gap:
                    ph.append(cur); cur = []
                cur.append(w)
            ph.append(cur)
            mel = melody(wav, ph)
        else:
            mel = None
    if len(words) < 30:
        raise SystemExit(f"{path}: only {len(words)} words recognised; not enough to measure")
    gaps = [b.start - a.end for a, b in zip(words, words[1:])]
    phrases, cur = [], [words[0]]
    for g, w in zip(gaps, words[1:]):
        if g >= phrase_gap:
            phrases.append(cur)
            cur = []
        cur.append(w)
    phrases.append(cur)
    pw = [len(p) / ((p[-1].end - p[0].start) / 60) for p in phrases if len(p) >= 4 and p[-1].end > p[0].start]
    span = words[-1].end - words[0].start
    inside = sum(w.end - w.start for w in words)
    pauses = [g for g in gaps if g >= pause_gap]
    mins = span / 60
    return Rhythm(path.name, len(words), round(span, 1), round(len(words) / mins, 1),
                  round(len(words) / (inside / 60), 1), len(pw), round(pct(pw, .1), 1), round(pct(pw, .5), 1),
                  round(pct(pw, .9), 1), round(st.pstdev(pw) / st.mean(pw), 3) if len(pw) > 1 else 0.0,
                  round(len(pauses) / mins, 1), round(pct(pauses, .5), 2), round(pct(pauses, .9), 2),
                  round(sum(g >= 0.6 for g in gaps) / mins, 1), *(mel or (None, None, None)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--seconds", type=int, default=180)
    ap.add_argument("--pause-gap", type=float, default=0.15)
    ap.add_argument("--phrase-gap", type=float, default=0.25)
    ap.add_argument("--model", default="medium")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--pitch", action="store_true", help="also measure melody sameness per phrase")
    args = ap.parse_args()
    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    rows = []
    for f in args.files:
        r = measure(f, model, args.seconds, args.pause_gap, args.phrase_gap, args.pitch)
        rows.append(r)
        print(json.dumps(asdict(r)), flush=True)
    if args.json:
        args.json.write_text(json.dumps([asdict(r) for r in rows], indent=1) + "\n")


if __name__ == "__main__":
    main()
