# EP006: Qwen3-VL local OCR, scored by whole lines

**Needs:** [ollama](https://ollama.com) with the vision models pulled. The scorer compares
`qwen3vl:8b`, `qwen2.5vl:3b`, `minicpm-v` and `moondream`; edit the list in the script to
test others. The description probe also needs ImageMagick (`magick`) to make its blank image.

## 1. OCR, scored by exact lines: `vlm-ocr-score.py`

```bash
python3 vlm-ocr-score.py
```

It reads [`ocr_test.png`](ocr_test.png), five lines of shell commands whose ground truth is
exact because a script generated them, and reports **exact lines out of 5** next to character
similarity. The video's point: 98.9% of characters right still shipped two broken commands.
Temperature 0; each model is unloaded after its call (`keep_alive: 0`), because on a 10 GB
card a resident model starves the next one and its empty reply looks like a model failure.

## 2. Is the description a function of the image? `vlm-describe-probe.py`

```bash
python3 vlm-describe-probe.py qwen3vl:8b photo1.jpg photo2.jpg photo3.jpg
```

Use at least three different photos of your own. It runs three controls:

- **Positive:** the same image twice should give near-identical descriptions (checks the scorer).
- **Negative:** different images should overlap little (checks it isn't a template).
- **Blank:** a flat grey image. A confident scene description here means the output isn't
  looking at the input.

It sets `num_ctx` to 16384, because a 4-megapixel image costs about 4,000 image tokens and
the default 4,096 window fails with a bare HTTP 400.
