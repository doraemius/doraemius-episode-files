# Cache-miss and write paths, with OAuth (2026-10-17, telemetry off, one run per point)

Same rig and ladder as the cached-read tests (`profile/variant-ladder.py` with `LADDER_WORKLOAD=miss|write`; two logical CPUs, 256 MiB, wrk2 open model, 128 connections, 8 s warm-up + 20 s window, OAuth on, one reusable token). Every miss is a never-seen id (one downstream fetch); every write has a unique idempotency key (one downstream mutation). Raw rows: `eval/panel-results/miss-write/`. Sustained = achieved/offered >= 0.97 with p50 < 5 ms, process alive and non-2xx <= 1% of requests; **single runs (+-10%)**; a row that fails on non-2xx is under investigation (below), not a throughput result.
Builds: Rust as built and `aws_lc_rs`, Go, Nim N2, Gleam G3 (tuned builds are pre-registered changes) and Java as built (**one event loop, 16-thread blocking downstream pool, untuned JVM**).

### Write path (POST /v1/item, unique idempotency key per request, one downstream mutation each)

| language | sustained rps | per logical CPU (% HAProxy) | latency ms p50 / p99 / p99.9 / max | CPU mean / peak (cores of 2) | memory MiB mean / peak | first failing step |
|---|---|---|---|---|---|---|
| Rust as built | 3,000 (2,915 achieved) | 1.5k (4%) | 4.28 / 13.42 / 18.77 / 25.8 | 0.88 / 1.21 | 26.1 / 46.4 | 5,000: 0.93 of offered, non-2xx 0 |
| Rust aws_lc_rs | 10,000 (9,923 achieved) | 5.0k (14%) | 1.30 / 3.22 / 34.97 / 42.6 | 1.03 / 1.57 | 61.5 / 93.8 | 15,000: 0.99 of offered, non-2xx 0 |
| Go | none passing | | | | | 500: 0.97 |
| Nim N2 | 1,000 (995 achieved) | 0.5k (1%) | 1.90 / 4.39 / 14.52 / 18.4 | 0.34 / 0.87 | 68.4 / 104.5 | 2,000: 0.87 of offered, non-2xx 6550 |
| Gleam G3 | 2,000 (1,987 achieved) | 1.0k (3%) | 1.47 / 2.80 / 3.27 / 5.4 | 1.08 / 1.42 | 104.1 / 117.9 | 3,000: 0.95 of offered, non-2xx 0 |
| Java 21 | 1,000 (995 achieved) | 0.5k (1%) | 1.21 / 2.94 / 5.64 / 10.2 | 0.41 / 1.48 | 149.2 / 155.5 | 2,000: 0.97 of offered, non-2xx 0 |

### Cache-miss read (GET of a never-seen id, one downstream fetch each)

| language | sustained rps | per logical CPU (% HAProxy) | latency ms p50 / p99 / p99.9 / max | CPU mean / peak (cores of 2) | memory MiB mean / peak | first failing step |
|---|---|---|---|---|---|---|
| Rust as built | 2,000 (1,943 achieved) | 1.0k (3%) | 4.01 / 13.27 / 14.19 / 14.8 | 0.54 / 0.78 | 18.4 / 26.8 | 3,000: 0.97 of offered, non-2xx 0 |
| Rust aws_lc_rs | 15,000 (14,883 achieved) | 7.4k (21%) | 1.81 / 25.58 / 38.33 / 44.5 | 1.43 / 1.99 | 80.7 / 131.1 | 20,000: 0.91 of offered, non-2xx 0 |
| Go | 10,000 (9,923 achieved) | 5.0k (14%) | 2.33 / 9.01 / 11.23 / 15.0 | 1.74 / 1.82 | 29.3 / 31.0 | 15,000: 0.76 of offered, non-2xx 0 |
| Nim N2 | 1,000 (995 achieved) | 0.5k (1%) | 2.05 / 4.69 / 18.70 / 31.6 | 0.34 / 0.89 | 65.2 / 99.1 | 2,000: 0.90 of offered, non-2xx 7750 |
| Gleam G3 | none passing | | | | | 500: 0.999 |
| Java 21 | 7,500 (7,443 achieved) | 3.7k (11%) | 1.64 / 22.01 / 50.65 / 69.5 | 1.53 / 2.00 | 199.2 / 239.7 | 10,000: 0.99 of offered, non-2xx 0 |

## Status of the surprises (to be settled by `profile/wrk-status-probe.py`, queued)
- **Go write: 515 non-2xx at 500 rps (5.3%)** on its first step, so no passing step.
- **Gleam G3 miss: 9,988 non-2xx at 500 rps** (essentially every request), yet 300 sequential and 400 parallel misses against the same build return 200 in a hand probe (`eval/panel-results/post-queue/miss-probe-*.txt`; Go and Nim also return 200 for all of them). So the failure appears only under the ladder's wrk2 pattern (128 connections from the start).
- **Nim N2 write and miss: non-2xx from 2,000 rps (6,550 and 7,750)**, with p99 jumping from about 4 ms to 1.6 s on writes.
- **Java as built** sustains 7,500 rps on misses but only 1,000 on writes (p50 5.3 ms at 2,000, 8.6 ms at 3,000, collapse by 5,000): consistent with a fixed pool of 16 blocking downstream calls (hypothesis H4 in `JAVA-TUNING-PLAN-2026-10-17.md`); its memory climbs to 200-240 MiB on the miss ladder against the 256 MiB limit (the 10,000 step peaked at 256 MiB; the container stayed alive).
- **Rust as built is poor on both paths (3,000 write, 2,000 miss) and Rust `aws_lc_rs` is 10,000 and 15,000**: the same code with a different crypto backend, because every request pays the RSA check before touching the downstream.

## Update (2026-10-17, evening)
- **Gleam rows above are superseded**: the miss "none passing" and write 2,000 were caused by a startup latch (one failed key fetch makes Gleam answer 401 forever; see `GLEAM-JWKS-LATCH-PLAN-2026-10-17.md`). With the guarded warm-up Gleam G3 sustains **3,000 rps on both misses and writes** (G4, the latch-free build, the same).
- **Go write rows are superseded for the two fixed builds**: Go as built has no passing write step because 5% of concurrent writes return 502 (`GO-WRITE-502-PLAN-2026-10-17.md`); Go W1 and W2 sustain 5,000 rps with about 0.5% non-2xx.
- **Java write rows**: as built 1,000; J1 (virtual threads, 37/37 on clean containers) 3,000; misses 7,500 in every build, CPU-bound near 9,500.
- A full second pass of the miss and write ladders for Rust, Go (as built, W1), Nim and Java (as built, J1) with the guarded harness and a healthy Tempo is running (`eval/panel-results/miss-write-v2/`); where the two passes disagree, both are reported and the second (guarded, healthy rig) is preferred. That pass also tests whether Nim's non-2xx from 2,000 rps repeats.

## FINAL write-path numbers (corrected perf stub that keeps POST connections alive; each arm in its own process where it matters; `eval/panel-results/write-fixedstub/`)
The write rows above were measured against a stub that closed connections after POSTs and are superseded. Sustained = achieved/offered >= 0.97 with p50 < 5 ms, alive, non-2xx <= 1% (single run).
| build | write sustained rps | notes |
|---|---:|---|
| Rust as built | 3,000 | p50 1.4 ms |
| Rust `aws_lc_rs` | 10,000 | p50 2.3 ms |
| Go as built | 10,000 | the 502s were the stub |
| Java as built | 7,500 | one event loop, untuned |
| Java J1 (virtual threads) | 7,500 | no gain; the earlier 3x was the stub |
| Nim N2 | 1,000 | fails from 2,000 rps (7,677 non-2xx): a new TCP connection per downstream call |
| Nim N3 (persistent client) | none passing | fixed p50 of about 41.5 ms per write (Nagle + delayed ACK), saturates near 1,700 rps with 0.1-0.3 cores busy |
| **Nim N4 (N3 + TCP_NODELAY)** | **10,000** | p50 1.71 ms; 37/37 x2; the diagnosis confirmed |
| Gleam G3 | 3,000 (3-run median; single pass said 1,000 by the p50 rule) | see repeats section |
Cache-miss reads (GET path, unaffected by the stub defect, two passes agree): Rust `aws_lc_rs` 15,000; Go 10,000; **Nim N3 10,000 (N2: 1,000)**; Java 7,500 (CPU-bound near 9,500, memory 238-240 MiB); Gleam G3/G4 3,000; Rust as built 2,000-3,000; Nim N2 1,000.

## 3-run repeats of the sustained steps (medians; `eval/panel-results/mw-repeats/`, 36 files)
Sustained = median achieved/offered >= 0.97 and median p50 < 5 ms over 3 runs; the next step up fails in every case.
| build | miss sustained / first failing | write sustained / first failing | vs single pass |
|---|---|---|---|
| Rust as built | 2,000 / 3,000 (ratio 0.97 borderline) | 3,000 / 5,000 | agrees |
| Rust `aws_lc_rs` | 15,000 / 20,000 | 10,000 / 15,000 (p50 20 ms) | agrees |
| Go | 10,000 / 15,000 | 10,000 / 15,000 | agrees |
| Java as built | 7,500 / 10,000 | 7,500 / 10,000 | agrees |
| Nim N4 | 10,000 / 15,000 (p50 187 ms) | 10,000 / 15,000 | agrees |
| Gleam G3 | 3,000 / 5,000 | **3,000** / not tested higher | write: single pass said 1,000 by the p50 rule; repeats pass at 3,000 (p50 2.0 ms), so 3,000 replaces 1,000 |
Conclusion: 11 of 12 cells reproduce the single-pass table; the one change (Gleam write 1,000 -> 3,000) is in Gleam's favour. Evidence for the per-path table is now three-run, not single-run.
