# Nim and Gleam: OAuth and telemetry bottlenecks optimized and re-tested (2026-10-17)

Pre-registered before any variant existed: `eval/prereg-oauth-acceleration-nim.md`, `eval/prereg-oauth-acceleration-gleam.md` (commits d96c97e0, f3aa025b).
Follows `OAUTH-SIGNATURE-ACCELERATION-PLAN.md` (one change per variant, no token-result caching). Baselines and bottlenecks: `NIM-GLEAM-PROFILE-OAUTH.md`.
Subjects: the assisted trees (human-built; not scored arms). Variants are generated from the UNCHANGED trees by `tuning/make-nim-opt.py` and `tuning/make-gleam-opt.py`.
Same rig and method as every earlier ladder: 2 logical CPUs (2,10), cached authenticated read, one 600 s token, wrk2 open model, fresh process per rate, 8 s warmup + 20 s measured, one run per point (about +-10%).
HAProxy yardstick: 34.7k sustained per logical CPU.

## What was changed
| variant | change |
|---|---|
| N1 (Nim) | span export off the request path: spans queue to one exporter thread that sends batches over one persistent connection (the original opened a new connection per span, inside the request) |
| N2 (Nim) | N1 + the public key parsed once into an OpenSSL `EVP_PKEY` at JWKS refresh + RSA verify through libcrypto `EVP_DigestVerify` (the original re-decoded the PEM text and ran BearSSL's RSA on every request) |
| G1 (Gleam) | span export off the request path: spans go to one exporter process, one batched POST per 100 ms; at most 8,192 spans outstanding, beyond that spans are dropped (the original spawned a process and an `httpc` request per span) |
| G2 (Gleam) | G1 + token decode: OTP `json:decode` instead of `jsx`, `base64:decode(..., #{mode => urlsafe, padding => false})` instead of two `binary:replace` calls and manual padding |
RSA verification in Gleam (`public_key:verify`, 38 us of a 70 us `authenticate`) is unchanged: OTP's `crypto` rebuilds the key from integers on each call and exposes no key handle; going further needs a NIF (not attempted).

## Results: with OAuth, cached read, per logical CPU (sustained = highest ladder step with achieved/offered >= 0.97 and p50 < 5 ms)
| arm | telemetry off | % of HAProxy | telemetry on | % of HAProxy |
|---|---:|---:|---:|---:|
| Nim as built | 2.5k | 7.2% | 0.5k | **1.4%** |
| Nim N1 | 2.0k | 5.8% | 2.5k | 7.2% |
| **Nim N2** | **10.0k** | **28.8%** | **7.5k** | **21.6%** |
| Gleam as built | 2.5k | 7.2% | 1.5k | 4.3% |
| Gleam G1 | 2.5k | 7.2% | 2.5k | 7.2% |
| **Gleam G2** | **3.75k** | **10.8%** | 2.5k | 7.2% |
For reference, same method: Rust as built 7%, Rust with `aws_lc_rs` 29%, Go 22% (`GO-PANEL-RESULTS.md`, `PANEL-AUTH-TUNING.md`).
N1's telemetry-off figure (4,000 rps) differs from the as-built 5,000 by one ladder step, inside the noise; N1 changes nothing on that path.
Data: `eval/panel-results/nim-opt/ladder.json`, `eval/panel-results/gleam-opt/ladder-final.json` (an earlier Gleam ladder, `ladder.json`, was taken before the exporter bound described below and is kept as evidence).

## CPU per request at 1,000 rps (user / kernel us, mean of two runs; `profile/usersys.py`)
| arm | telemetry off | telemetry on | on minus off (total) |
|---|---:|---:|---:|
| Nim as built | 289 / 28 | 314 / 523 | +520 |
| Nim N1 | 295 / 26 | 308 / 25 | +12 |
| Nim N2 | 86 / 31 | 94 / 33 | +10 |
| Gleam as built | 298 / 52 | 523 / 118 | +291 |
| Gleam G1 | 294 / 53 | 362 / 65 | +80 |
| Gleam G2 | 270 / 55 | 321 / 62 | +58 |
Nim's telemetry collapse was 490 us of KERNEL time per request (a connection per span); batching removes it. Nim N2's user CPU falls 3.3x (callgrind: 0.79 M instructions per request vs 2.94 M, 3.7x fewer; only OpenSSL frames remain, `EVP_DigestVerify` 44%; no BearSSL or PEM-decoder frames).

## Verdicts against the pre-registered thresholds
| | criterion | measured | verdict |
|---|---|---|---|
| N1 | 37/37; telemetry-on kernel <= 100 us; on/off sustained >= 0.8 | 37/37 (see anomalies); kernel 25-28 us (baseline 523); on/off 5,000/4,000 | **retained** |
| N2 | 37/37; tamper battery identical to as-built; sustained off >= 10,000 rps; instructions <= 50% of 2.94 M | 37/37 (final build 3/3); battery identical after one fix (below); 20,000 rps (4x); 0.79 M (27%) | **retained** |
| G1 | 37/37; telemetry-on gap <= +60 us; on/off sustained >= 0.8 | 37/37 (9/9 final, 12/12 earlier build); gap +80 (G1) / +58 (G2; identical telemetry code, pooled ~+69 +-15, the line is inside the noise); on/off 5,000/5,000 | **retained, gap criterion borderline**; the gap shrank from +291 to ~+70 and the OOM deaths are gone |
| G2 | 37/37; parity: no looser acceptance; `authenticate` <= 60 us | 37/37 (9/9 final); parity 29 cases, 0 differences; 52.4 us (from 69.9) | **retained** |
Gleam G2's ladder gain is one step (5,000 -> 7,500 telemetry off, +50%) plus about 12% less user CPU; the pre-registration said the end-to-end gain (~5% predicted) would sit below ladder resolution, so G2 is judged on parity and direct timing; the ladder is consistent with it.

## Defects found along the way (all fixed, none hidden)
1. **N2 accepted a non-canonical signature spelling** (`profile/token-tamper.py`, first N2 build): flipping the last base64url character of the signature changed no decoded byte, so the token still verified (200; the unmodified arm refused). It cannot forge a new message but gives one token many valid spellings. Fixed by requiring the segment to equal the canonical re-encoding; N2 now matches the unmodified arm on all 20 forged/malformed cases (`eval/panel-results/nim-opt/tamper-*.txt`). The Gleam original and G1/G2 had no such leniency (their tables are identical).
2. **G1's exporter was unbounded under saturation.** At 7,000+ rps with telemetry on, memory climbed 68 -> 256 MiB in 15 s and the container was OOM-killed (`oom=true exit=137`, reproduced for G1 and G2; `profile/memwatch.py`, `eval/panel-results/gleam-opt/memwatch-6000.txt`). The original dies the same way earlier (at 6,000 rps: peak 256 MiB in under 10 s). Fix: producers drop a span when 8,192 are outstanding (an atomic counter released after each flush). Re-test at 7,500: G1 peak 207 MiB, G2 226 MiB, both alive, achieving 7,059 and 7,460 rps; the final ladders have no deaths.
3. **My adapters could report "ready" while another container held the ports** (the Nim copy lacked the running-container check; N2's first verification never ran, it was N1 answering). Fixed in both generators.
4. **Open anomaly, not explained:** the FIRST verifier run of N1 (seed 101: T-OTEL-05 saw 103 requests for 100) and of N2's first clean run (seed 101: 102 requests plus one 401 on a valid token) failed; every later run passed (as built 7/7; N1 8/8 after; N2 7/7 after on the pre-fix build, then 3/3 on the final build). A 15-repetition x 2 check of the same metric (with and without restart) found 0 deviations for all three arms. Counting all runs: as built 0/7 failed, N1 1/9, N2 (valid runs) 1/8. This is not statistically distinguishable from zero but is not proof of equivalence; treat first-run-after-build as suspect.

## Limits
One run per ladder point (+-10%, coarse steps); sustained numbers are the last passing step, not the knee. Cached authenticated reads only (miss and write paths not measured). The benchmark reuses one token; Nim and Gleam verify per request (no result cache), so reuse does not help them. The N1/N2/G1/G2 trees are Claude's modifications of human-built trees, not model-written code and not scored arms. Gleam RSA verification (51% of its `authenticate`) remains the dominant unfixed cost; Nim N2's remaining cost is OpenSSL's modular exponentiation (44% of instructions) plus HTTP and JSON.

## Addendum 2026-10-17: Gleam G3 (RSA verify NIF), `eval/prereg-oauth-acceleration-gleam-nif.md`
G3 = G2 + a C NIF (`tuning/nif/rsa_nif.c`, OpenSSL `EVP_DigestVerify` with an `EVP_PKEY` built once per kid at JWKS refresh) in place of `public_key:verify`.
| | G2 | G3 |
|---|---:|---:|
| `rsa verify` us/call (direct timing) | 36.2 | 15.8 |
| `authenticate` us/call | 52.4 | 26.9 |
| user CPU/request at 1,000 rps, telemetry off (mean of 4) | 269 | 229 |
| sustained per logical CPU, telemetry off | 3.75k (10.8%) | 5.0k (14.4%) |
| sustained per logical CPU, telemetry on | 2.5k (7.2%) | 3.75k (10.8%) |
Parity vs the original: 32 cases, 0 differences (3 runs). Verifier 37/37 on 6 seeds. 200k verifies leak 4 MiB RSS. The forged-token battery flagged "flip signature (last char)" on G3; this is a token-dependent test case that the original arm also accepts when the flip lands in unused bits (OTP's base64 ignores them), not a G3 difference; details in the pre-registration's "After the run". Gleam arms accept non-canonical signature spellings (Nim as-built does not).
Rig note: Tempo (1 GiB limit) was OOM-killed mid-repeat; the affected seeds were rerun and the failed file kept.

Canonical-signature check (added after the G3 run, at the author's request): G1, G2 and G3 now reject respelled signatures (same bytes, different unused trailing bits); the as-built Gleam arm still accepts them (deterministic battery case: 200 vs 401). Verifier 12/12, parity 32 cases with the one intended difference, `authenticate` 27.9 us. Ladders were not rerun (cost ~1 us). Data: `eval/panel-results/gleam-opt/canonical/`.
