# 3-run medians for the headline points (2026-10-17, telemetry off)

Three fresh-process runs at each stack's sustained step and the next step up (`eval/panel-results/repeats/rep<N>-<arm>.json`, script `profile/repeats-report.py`; same rig, 100 ms cgroup sampling, wrk2 open model, 8 s warm-up + 20 s window). A step is "sustained" when the MEDIAN achieved/offered is >= 0.97 and the median p50 is < 5 ms; the per-run ratios are printed so a step where one run fails (for example Rust without OAuth at 60,000: 0.97, 0.99, 0.95) is visible. Latency columns are medians over the three runs (wrk2 resolves latency to about +-1 ms).
These replace the single-run values wherever the video, the decision guide or the tables quote a sustained rate.

### No OAuth (full service, token check bypassed)

| language | sustained step (runs) | achieved rps median (min-max) | per logical CPU (% HAProxy) | latency ms p50 / p99 / p99.9 / max (medians) | CPU cores mean / peak | memory MiB mean / peak | achieved/offered per run at this step | next step up: achieved/offered per run |
|---|---|---|---|---|---|---|---|---|
| Rust | 60,000 (3 runs) | 58,258 (56,980-59,524) | 29.1k (84%) | 1.40 / 3.37 / 3.85 / 4.7 | 1.35 / 1.49 | 8.5 / 9.4 | 0.97, 0.99, 0.95 (median passes, a run fails) | 0.95, 0.94, 0.98 @ 80,000 |
| Go (full) | 45,000 (3 runs) | 44,645 (44,644-44,646) | 22.3k (64%) | 1.66 / 5.11 / 6.98 / 11.7 | 1.88 / 1.96 | 10.9 / 12.8 | 0.99, 0.99, 0.99 (all runs pass) | 0.75, 0.77, 0.75 @ 60,000 |
| Go (HTTP only) | 60,000 (3 runs) | 59,525 (59,524-59,527) | 29.8k (86%) | 1.48 / 4.23 / 5.37 / 7.8 | 1.71 / 1.81 | 9.4 / 10.4 | 0.99, 0.99, 0.99 (all runs pass) | 0.85, 0.85, 0.84 @ 80,000 |
| Nim (as built) | 45,000 (3 runs) | 44,644 (44,641-44,644) | 22.3k (64%) | 1.88 / 3.94 / 4.44 / 5.3 | 1.34 / 1.38 | 10.5 / 11.3 | 0.99, 0.99, 0.99 (all runs pass) | 0.85, 0.85, 0.84 @ 60,000 |
| Gleam (as built) | 10,000 (3 runs) | 9,923 (9,711-9,924) | 5.0k (14%) | 1.41 / 3.19 / 3.68 / 5.0 | 1.42 / 1.56 | 72.6 / 74.8 | 0.99, 0.99, 0.97 (all runs pass) | 0.99, 0.99, 0.97 @ 15,000 |
| Java 21 | 80,000 (3 runs) | 79,362 (79,359-79,364) | 39.7k (114%) | 1.57 / 4.88 / 7.66 / 44.6 | 0.96 / 1.94 | 112.6 / 116.5 | 0.99, 0.99, 0.99 (all runs pass) | 0.85, 0.85, 0.85 @ 100,000 |

### With OAuth

| language | sustained step (runs) | achieved rps median (min-max) | per logical CPU (% HAProxy) | latency ms p50 / p99 / p99.9 / max (medians) | CPU cores mean / peak | memory MiB mean / peak | achieved/offered per run at this step | next step up: achieved/offered per run |
|---|---|---|---|---|---|---|---|---|
| Rust as built | 5,000 (3 runs) | 4,855 (4,750-4,963) | 2.4k (7%) | 4.76 / 10.77 / 11.98 / 13.2 | 1.33 / 1.51 | 7.6 / 8.4 | 0.99, 0.97, 0.95 (median passes, a run fails) | 0.75, 0.74, 0.75 @ 7,500 |
| Rust aws_lc_rs | 20,000 (3 runs) | 19,423 (18,996-19,844) | 9.7k (28%) | 1.59 / 3.40 / 4.07 / 4.5 | 1.20 / 1.27 | 8.0 / 8.6 | 0.95, 0.97, 0.99 (median passes, a run fails) | 0.78, 0.78, 0.79 @ 30,000 |
| Go | 15,000 (3 runs) | 14,884 (14,566-14,884) | 7.4k (21%) | 1.40 / 3.52 / 4.88 / 8.1 | 1.67 / 1.76 | 11.4 / 13.4 | 0.97, 0.99, 0.99 (all runs pass) | 0.87, 0.89, 0.89 @ 20,000 |
| Nim N2 | 20,000 (3 runs) | 19,843 (19,420-19,844) | 9.9k (29%) | 2.07 / 4.47 / 5.49 / 7.9 | 1.86 / 1.90 | 17.8 / 18.6 | 0.99, 0.97, 0.99 (all runs pass) | 0.66, 0.67, 0.66 @ 30,000 |
| Gleam G3 | 10,000 (3 runs) | 9,923 (9,709-9,923) | 5.0k (14%) | 1.91 / 10.52 / 15.61 / 23.1 | 1.92 / 2.01 | 72.4 / 75.0 | 0.99, 0.99, 0.97 (median passes, a run fails) | 0.69, 0.69, 0.68 @ 15,000 |
| Java 21 | 20,000 (3 runs) | 19,420 (19,419-19,843) | 9.7k (28%) | 1.77 / 3.58 / 4.07 / 5.0 | 0.90 / 1.63 | 112.9 / 121.1 | 0.97, 0.99, 0.97 (all runs pass) | 0.74, 0.75, 0.74 @ 30,000 |


## What the repeats changed
- Sustained steps agree with the single runs for Rust, Go, Nim, Java and every OAuth build. The spread inside a step is small (for example Go 44,644-44,646, Java 79,359-79,364) because the load is open-loop at a fixed rate; the knee is decided by which step passes, so the steps themselves are the coarse part (+-10% between neighbours).
- **Gleam without OAuth is 10,000 (14%), not 5,000**: the single run had landed on the knee (0.95 at 10k); all three repeats pass it (0.97-0.99). Gleam G3 with OAuth sustains the same 10,000.
- **Rust as built under OAuth is borderline at its step**: p50 4.76 ms median at 5,000 rps (limit 5 ms), and the next step collapses (0.74-0.75).
- **Java's tail is spikier than the single run showed**: no-OAuth at 80,000 the median p99.9 is 7.66 ms and the median max 44.6 ms (single run 3.82 / 5.1); mean CPU is 0.96 cores with a 1.94 peak. This fits the JIT/GC-burst hypothesis in `JAVA-TUNING-PLAN-2026-10-17.md`.
- Nim's no-OAuth sustained rate is 45,000 in all three repeats (the earlier session's 59.5k is not reproduced today; still unexplained).
- Not repeated: the common-rate (10,000 / 5,000 rps) tables and the per-request CPU figures; those stay single-run.
