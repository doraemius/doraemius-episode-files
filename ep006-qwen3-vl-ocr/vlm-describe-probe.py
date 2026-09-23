#!/usr/bin/env python3
"""EP006 gate 2 (Doraemius): is Qwen3-VL's free-text description a function of the image?

Three controls, because a templated describer and a real one look identical on one sample:
  POSITIVE  same image twice, temp 0  -> must be near-identical (scorer sanity)
  NEGATIVE  six different images      -> pairwise overlap must be LOW
  BLANK     a flat grey image         -> a confident scene description here means the
                                         output is not a function of the input
"""
import base64, json, urllib.request, time, re, itertools, subprocess, sys

# usage: python3 vlm-describe-probe.py MODEL IMG1 IMG2 IMG3 [...]   (use your own photos)
if len(sys.argv) < 5:
    sys.exit("usage: vlm-describe-probe.py MODEL IMG1 IMG2 IMG3 [...]  (at least 3 different images)")
MODEL = sys.argv[1]
IMGS = sys.argv[2:]
subprocess.run(["magick", "-size", "800x600", "xc:gray50", "/tmp/blank.png"], check=True)

STOP = set("a an the is are was were of in on at to and or with this that it its there "
           "for from by as be been being image picture photo shows showing depicts "
           "featuring appears scene s t".split())
def words(s):
    return {w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP and len(w) > 2}
def jac(a, b):
    A, B = words(a), words(b)
    return len(A & B) / len(A | B) if A | B else 0.0

def ask(path, t=600):
    img = base64.b64encode(open(path, "rb").read()).decode()
    req = urllib.request.Request("http://localhost:11434/api/generate",
        data=json.dumps({"model": MODEL, "prompt": "Describe this image in two sentences.",
                         "images": [img], "stream": False,
                         "options": {"temperature": 0, "seed": 1, "num_ctx": 16384}}).encode(),
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        return json.load(urllib.request.urlopen(req, timeout=t))["response"].strip(), time.time() - t0
    except urllib.error.HTTPError as e:      # a 4 MP image costs >4k tokens; default n_ctx is 4096
        return f"__HTTP{e.code}__ {e.read()[:160]}", time.time() - t0

print(f"model={MODEL}\n")
descs = {}
for p in IMGS:
    d, dt = ask(p)
    descs[p] = d
    print(f"[{dt:4.1f}s] {p.split('/')[-1][:44]:44s} {d[:88]}")

rep, _ = ask(IMGS[0])
pos = jac(descs[IMGS[0]], rep)
blank, _ = ask("/tmp/blank.png")
pairs = [jac(descs[a], descs[b]) for a, b in itertools.combinations(IMGS, 2)]
bl = [jac(blank, descs[p]) for p in IMGS]

print(f"\nPOSITIVE control (same image twice)      Jaccard {pos:.2f}   want >0.80")
print(f"NEGATIVE control (6 different images)    Jaccard mean {sum(pairs)/len(pairs):.2f} "
      f"max {max(pairs):.2f}   want <0.30")
print(f"BLANK control vs real images             Jaccard mean {sum(bl)/len(bl):.2f}   want low")
print(f"\nBLANK image description:\n{blank[:300]}")
