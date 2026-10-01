# Does AI share your data? — the runnable test

Companion code for the Doraemius video **"Does AI share your data?"** This is the measured
red-team instrument behind the episode: does a consumer-style LLM agent **leak the data you give
it** when a hidden instruction is buried in the content it reads — and can code-level defenses
stop it? Every prompt, number, and script is here so you can reproduce it.

> **Authorized, isolated use only.** Everything targets `127.0.0.1`: a throwaway
> [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/) container (built to be attacked)
> and a local decoy that never talks to the internet. All secrets are **fake**, all PII is
> **synthetic**. Do **not** point any of it at systems you don't own. It contains **no working
> exploit payloads** — the artifact we record is the model's *response*, not an attack.

## What it measures

- **Leak via indirect prompt injection (P1–P5)** — the hidden instruction arrives through a
  planted document, a hostile tool description, a poisoned retrieved chunk, a chained read, or a
  reinforced variant. "Obeyed" = a planted synthetic secret reaches a loopback decoy sink — a
  fact read from the sink's own state, never an LLM judge. (`injections.py`)
- **Direct exfiltration, memorization, PII handling (C5–C8)** — exfil via tools, the
  Nasr/Carlini divergence attack, and private-data mishandling. C6 is graded against a frozen
  rubric (`score_c6.py`).
- **Defenses, before/after** — the same battery under: naked → a RAG policy preamble → a
  guardrail proxy (regex scanner; swap in LLM Guard) → deterministic PreToolUse/PostToolUse
  hooks. The point is the gap where a model is *willing* but code makes it *unable*. (`defenses.py`)

## Files

| File | Role |
|---|---|
| `prompts.py` | The battery as data: 12 technique wrappers × threat counts (C1–C9) + injection counts (P1–P5). |
| `injections.py` | Indirect-injection delivery (P1–P5) + cover tasks. |
| `executor.py` | ReAct agent loop against the loopback sandbox (hard loopback guard + hooks). |
| `defenses.py` | E1 RAG preamble · E3 guardrail proxy · E2 deterministic hooks. |
| `clients.py` | Minimal OpenAI-compatible `/v1/chat/completions` client. |
| `run_eval.py` | Iterates models × counts × techniques × defense conditions; auto-scores, formal success checks. |
| `score_c6.py` | C6 memorization grader (frozen detect + confirm rubric). |
| `challenge_check.py` | Formal Juice Shop challenge-state success check (C1/C2/C4). |
| `honeypot_proxy.py` | Loopback-only decoy proxy / sink; logs every request, never forwards. |
| `docker-compose.yml` | Juice Shop target, bound to loopback only. |
| `selftest_injection.py` | Offline self-test (no model, no GPU) — proves the scoring before any run. |
| `verify_injection.py`, `aggregate_injection.py` | Hand-verification + result aggregation. |
| `run-config.example.json` | Template — copy to `run-config.json` (gitignored) and fill your own model endpoints. |

## Run it

```bash
# 0. prove the instrument offline (no model needed)
python3 selftest_injection.py          # exit 0 = obeyed/flagged/E2-block all score correctly

# 1. target + decoy sink (separate terminals)
docker compose up -d                                   # Juice Shop on 127.0.0.1:3000
python3 honeypot_proxy.py --port 8890 --log sink.jsonl # loopback decoy sink

# 2. configure + run (models are anonymized A–D in your own config)
cp run-config.example.json run-config.json             # fill model endpoints; keys via env vars
python3 run_eval.py --config run-config.json --out results.jsonl --execute
python3 score_c6.py results.jsonl                      # grade the memorization leg
```

## Grounded in the research
- AgentDojo — https://arxiv.org/abs/2406.13352
- InjecAgent — https://arxiv.org/abs/2403.02691
- Extracting Training Data (Nasr/Carlini) — https://arxiv.org/abs/2311.17035
- StrongREJECT — https://arxiv.org/abs/2402.10260

Narration in the video is AI-generated; all provider/model/tool names are anonymized. Tests run
locally in an isolated sandbox with synthetic data.
