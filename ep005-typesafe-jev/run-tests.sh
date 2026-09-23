#!/usr/bin/env bash
# EP005 — TypeSafe's Jev AI Model, Self-Hosted (Doraemius). Runs the three test inputs
# against jeff, the MIT-licensed open reproduction of Jev's API, on your own GPU.
set -euo pipefail
export PY_MEM_CAP=none                                    # only if your python3 is a memory-capped wrapper
curl -LsSf https://astral.sh/uv/install.sh | sh          # uv: fast Python package manager
git clone https://github.com/logan-markewich/jeff && cd jeff && uv sync
JEFF_API_KEYS=devkey JEFF_PORT=8010 nohup uv run jeff > jeff.log 2>&1 &
until curl -s localhost:8010/healthz | grep -q '"ok":true'; do sleep 2; done
for q in charmin fomc support; do
  echo "== $q"
  curl -s localhost:8010/v1/systemone -H 'Authorization: Bearer devkey' \
       -H 'Content-Type: application/json' -d @../${q}_query.json \
    | jq '.answers | map_values(del(.legend,.type))'
done
