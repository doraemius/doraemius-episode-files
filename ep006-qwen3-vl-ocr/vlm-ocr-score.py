#!/usr/bin/env python3
"""EP006 T4 gate: score local VLMs on OCR of a frame whose text is known exactly."""
import base64, json, urllib.request, time, difflib, re, sys
from pathlib import Path

# the test image sits next to this script; its text is GOLD below, generated, not typed
img = base64.b64encode((Path(__file__).resolve().parent / "ocr_test.png").read_bytes()).decode()
GOLD = ["$ export PY_MEM_CAP=none",
        "$ curl -LsSf https://astral.sh/uv/install.sh | sh",
        "$ git clone https://github.com/logan-markewich/jeff",
        "$ cd jeff && uv sync",
        "# one env var, one installer, one clone"]

def ask(model, prompt, t=600):
    t0 = time.time()
    req = urllib.request.Request("http://localhost:11434/api/generate",
        data=json.dumps({"model": model, "prompt": prompt, "images": [img], "stream": False,
                         # unload after each call: on a 10 GB card a resident 8B starves the
                         # next model and its empty reply looks like a model failure
                         "keep_alive": 0, "options": {"temperature": 0, "num_ctx": 8192}}).encode(),
        headers={"Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=t))["response"], time.time() - t0
    except Exception as e:
        return f"__ERROR__ {e}", time.time() - t0

norm = lambda s: re.sub(r"\s+", " ", s).strip()
print(f"{'model':20s} {'sec':>5} {'exact':>7} {'char':>6}   n=5 lines, temp=0, keep_alive=0")
for m in ("qwen3vl:8b", "qwen2.5vl:3b", "minicpm-v:latest", "moondream:latest"):
    txt, dt = ask(m, "Read all text in this image exactly. Output only the text.")
    lines = [norm(l) for l in txt.splitlines() if l.strip()]
    ratios = [max((difflib.SequenceMatcher(None, norm(g), l).ratio() for l in lines), default=0.0)
              for g in GOLD]
    exact = sum(r == 1.0 for r in ratios)
    flag = "  EMPTY/ERROR" if not lines or txt.startswith("__ERROR__") else ""
    print(f"{m:20s} {dt:5.1f} {exact:5d}/5 {100*sum(ratios)/len(ratios):5.1f}%{flag}")
