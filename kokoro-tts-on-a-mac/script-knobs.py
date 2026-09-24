#!/usr/bin/env python3
"""Measure a narration script's Humor and Human knobs.

Narration = lines starting with ">". A sentence tagged {H} is a joke (punchline, tag, comic line);
{U} carries a human touch (filler, beat before a reveal, self-aside). A tag applies to the sentence
it starts. Knob = tagged sentences / all narration sentences. Also prints words and the runtime
at 185 wpm (middle of the 173-200 band).

    python3 script-knobs.py narration.md --humor 33 --human 10

Exits 1 if a knob is more than --tolerance points from its target, so it can gate a build.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def sentences(md: str) -> list[str]:
    body = md.split("\n## Fact sources")[0]
    text = " ".join(l[1:].strip() for l in body.splitlines() if l.startswith(">"))
    return [s for s in re.split(r"(?<=[.?!…])\s+(?=\{|[A-Z\"'])", text) if s.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=Path)
    ap.add_argument("--humor", type=float, default=33)
    ap.add_argument("--human", type=float, default=10)
    ap.add_argument("--tolerance", type=float, default=4)
    args = ap.parse_args()
    ss = sentences(args.script.read_text())
    if not ss:
        sys.exit("no narration sentences found (lines starting with '>')")
    h = sum(s.lstrip().startswith("{H}") for s in ss)
    u = sum(s.lstrip().startswith("{U}") for s in ss)
    words = sum(len(re.sub(r"\{[HU]\}", "", s).split()) for s in ss)
    hp, up = 100 * h / len(ss), 100 * u / len(ss)
    print(f"{len(ss)} sentences, {words} words, ~{words / 185:.1f} min at 185 wpm")
    print(f"Humor {h}/{len(ss)} = {hp:.0f}% (target {args.humor:.0f}%)   Human {u}/{len(ss)} = {up:.0f}% (target {args.human:.0f}%)")
    bad = [n for n, got, want in (("Humor", hp, args.humor), ("Human", up, args.human)) if abs(got - want) > args.tolerance]
    if bad:
        sys.exit(f"off target: {', '.join(bad)} (tolerance {args.tolerance:.0f} points)")


if __name__ == "__main__":
    main()
