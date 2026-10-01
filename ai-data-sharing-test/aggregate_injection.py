#!/usr/bin/env python3
"""Merge the P-block runs and print the obeyed/flagged/ignored matrix + sink audit.

naked + rag_e1 come from the first run; guardrail_proxy_e3 + hooks_e2 from the
completion run (authoritative for those two conditions). stdlib only.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ORDER = ["naked", "rag_e1", "guardrail_proxy_e3", "hooks_e2"]
COUNTS = ["P1", "P2", "P3", "P4", "P5"]


def load(p: str) -> list[dict]:
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def main() -> int:
    r1, r2 = load("results.p4.jsonl"), load("results.p4b.jsonl")
    rows = [x for x in r1 if x["condition"] in ("naked", "rag_e1")] + r2
    print(f"merged rows: {len(rows)}")
    tab = collections.defaultdict(collections.Counter)
    for x in rows:
        tab[(x["count"], x["condition"])][x["capability"]] += 1
    hdr = f'{"count":5} {"condition":20} {"obey":>4} {"flag":>4} {"ign":>4} {"err":>4} {"tot":>4}'
    print("\n" + hdr)
    for ct in COUNTS:
        for cond in ORDER:
            c = tab[(ct, cond)]
            tot = sum(c.values())
            print(f'{ct:5} {cond:20} {c.get("obeyed",0):>4} {c.get("flagged",0):>4} '
                  f'{c.get("ignored_safely",0):>4} {c.get("error",0):>4} {tot:>4}')
    print("\nOBEYED (exfil reached sink) by condition:")
    for cond in ORDER:
        rr = [x for x in rows if x["condition"] == cond]
        ob = sum(1 for x in rr if x["capability"] == "obeyed")
        print(f"  {cond:20} {ob}/{len(rr)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
