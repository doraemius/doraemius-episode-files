# Profile: where the Rust control spends its CPU per request

Date 2026-10-16. Subject: `arms/rust-control` (source unchanged), cached authenticated read `GET /v1/item/panel-hot`.

## Result
**92.6% of all user-space instructions are RSA signature verification inside `jsonwebtoken`'s pure-Rust backend.**
Call chain (inclusive, % of 2.853 G instructions over 1,001 requests, i.e. ~2.85 M instructions/request):

| frame | inclusive |
|---|---|
| `AppState::authenticate` (`src/main.rs`) | 97.1% |
| `jsonwebtoken::decoding::decode` -> `verify_signature` | 96.5% -> 95.3% |
| `jsonwebtoken ... rust_crypto::rsa::Rsa256Verifier::verify` | 94.7% |
| `rsa-0.9.10 Pkcs1v15Sign::verify` | 93.1% |
| `num-bigint-dig::BigUint::modpow` -> `monty_modpow` | 92.6% |
| `num-bigint-dig::monty::montgomery` (the inner loop) | 89.4% |

Everything else is small: OpenTelemetry batch span export ~3%, SHA-256 of the signed payload 1.5%, claims JSON
parse ~0.9%, allocator ~3% combined. The HTTP stack (hyper/axum/tokio) is a few percent.

Corroboration: 2.85 M instructions/request at the measured ~240 us CPU/request is ~3.5 IPC at ~3.4 GHz, consistent with a
tight bigint multiply loop, and with `/healthz` costing ~25 us on the same box (no auth).

## Method (no root needed)
`perf` is installed but unusable: `perf_event_paranoid=4` and sudo needs a password. Used valgrind callgrind instead.
1. Debug-symbol copy of the control's source in a separate image (`CARGO_PROFILE_RELEASE_DEBUG=true`); the frozen arm image is untouched.
2. Run under `valgrind --tool=callgrind` in a container on the host network, rig up (perf route).
3. 30 warm requests (JWKS fetch, cache populate), `callgrind_control -z` to zero counters, then 1,001 requests at 25 rps
   (wrk2, 1 thread, 4 connections, 40 s) with a 600 s Keycloak token, then `callgrind_control -d` to dump.
4. `callgrind_annotate --inclusive=yes`. Exclusive attribution collapsed into the thread-start frame (stack unwinding
   under valgrind), so only the inclusive view is reported.
Valgrind counts instructions, not time; it is deterministic, so 25 rps is enough.

## What it means
- The ~190 us/request I could not place earlier IS the RSA modular exponentiation. It is not the HTTP server, not
  telemetry (3%), not locks.
- `jsonwebtoken` 10 with its RustCrypto backend (`rsa` + `num-bigint-dig`) is far slower than ring/aws-lc-rs/OpenSSL
  (OpenSSL RS256 2048-bit verify measured ~23 us on this host, ~10x less). Same service logic, different crypto crate.
- This is a dependency choice the arm made, an as-built default, per PLAN 5.1 recorded not fixed.
- It explains why the ceiling (~5.3k rps) is CPU-in-ALU-bound on a single SMT-paired physical core (bigint multiply
  gets little from a second hyperthread). It does NOT explain the residual ~30% logical-CPU idle at the ceiling.

## Not claimed
- That switching crypto backend would give a specific speedup: untested (video 2).
- That Nim or Gleam have the same hotspot: they use different libraries and were not profiled. Their auth path
  may be much cheaper, so "Rust is slower on cached reads" would be a statement about this crate, not the language.
- Cheap fixes also exist outside the library: cache verified tokens by hash until `exp`. Not measured.

## Addendum: it was the library choice - one feature flag moves the ceiling ~4x (measured)

The control's `Cargo.toml` has `jsonwebtoken = { version = "10", features = ["rust_crypto"] }`. `jsonwebtoken` offers two
backends, `aws_lc_rs` and `rust_crypto`, exactly one enabled (https://docs.rs/crate/jsonwebtoken/latest). The
`rust_crypto` backend is the pure-Rust `rsa` + `num-bigint-dig` path that the profile above shows burning 92.6% of CPU.
A competitor's README claims `rust_crypto` is substantially slower than `aws_lc_rs` (third party, unverified); the numbers
below are mine.

Experiment (scratch copy only; the frozen `arms/rust-control` is untouched): change that one feature to `aws_lc_rs`,
rebuild without `--locked`, repeat the identical callgrind protocol (1,001 requests at 25 rps).

| | `rust_crypto` (as built) | `aws_lc_rs` |
|---|---|---|
| instructions, 1,001 requests | 2.853 G (2.85 M/request) | 0.478 G (0.48 M/request) = **5.97x fewer** |
| RSA verify, per request | ~2.64 M instr | ~0.30 M instr = ~8.9x fewer |
| RSA share of all instructions | 92.6% | 62.3% (aws-lc `RSA_verify`) |

Capacity in the SAME 2-CPU box (CPUs 2,10; 256 MiB; OTel on; perf route; cached read; 15 s warmup + 30 s; one run per
rate, NOT a 3-run panel):

| offered rps | achieved | p50 / p99 ms | SUT CPU busy |
|---|---|---|---|
| 5,000 | 4,988 (99.8%) | 0.92 / 1.78 | 19% |
| 12,000 | 11,970 | 1.01 / 2.11 | 42% |
| 20,000 | 19,948 (99.7%) | 1.15 / 2.53 | 69% |
| 25,000 | 21,014 (84%) | 3,160 / 4,680 | 90% |

So the ceiling moves from ~5.3k to ~21k rps (**~4x**), and at the old ceiling the box now sits at 19% CPU instead of 70%.
With the bigint loop gone the service saturates at ~90% logical-CPU busy, in line with plain CPU saturation, which also
weakens the SMT-only reading of the earlier "30% idle at the ceiling" (an ALU-bound bigint loop on one SMT pair).

### Consequences
1. The "Rust cached-read ceiling" in `PANEL-CEILING-FINDING.md` is a statement about the **crypto crate this arm picked**,
   not about Rust. Any cross-language comparison on authenticated endpoints must say which JWT/RSA library each arm used.
2. This is exactly video 2's profiler-led tuning: profile (callgrind, no root), find a library-level hotspot, change one
   dependency feature, re-measure. It is also a strong "check the dependency before blaming the language" beat.
3. Still not done: the same swap on the miss/write paths (downstream hop included); a 3-run panel for the variant; profiling
   Nim and Gleam's JWT paths to see whether they have an equivalent hotspot or already use a fast native library.

## Rust B hardware-counter profile (2026-10-17)

The prior B callgrind result established the large instruction reduction, but this is a fresh profile of the rebuilt
AWS-LC B image on the Ryzen host. It uses ports `18080` (HTTP), `15051` (gRPC), and `19464` (metrics), deliberately outside
the concurrently used low-port range. The frozen contract verifier passed **37/37** rows first:
`eval/results/20261017T063010Z-rust-auth-b-awslc.json`.

After 100 authenticated warm-up requests, a privileged disposable profiler container attached `perf stat` to the live
Rust-B process. It counted 10,000 sequential authenticated cached reads, all HTTP 200:

| counter | total | per successful request |
|---|---:|---:|
| instructions | 5,267,499,636 | ~526,750 |
| cycles | 6,570,998,857 | ~657,100 |
| branches | 844,796,338 | ~84,480 |
| branch misses | 75,141,586 | ~7,514 |

The counter run is saved on the profiling host in
`eval/panel-results/rust-auth-b-profile-20261017-perf/perf.txt`; its request accounting is `load.json`.
The six events were multiplexed by the PMU (the counter report records 79--86% running time), so the totals are scaled
estimates, not cycle-exact figures. They nevertheless closely corroborate the earlier B Callgrind value of ~0.48 M
instructions/request.

An independent sampled call graph recorded 20,000 more authenticated reads (20,000 HTTP 200, 0 errors) and 3,000 lost-free
cycle samples. Its raw data and text report are `perf.data` and `perf-report.txt` in the same host directory. The leading
user-space leaf is AWS-LC's `aws_lc_0_46_0_bn_sqrx8x_internal` (6.94% exclusive samples); other AWS-LC Montgomery routines
include `aws_lc_0_46_0_bn_mulx4x_mont` (1.25%), `bn_mul_add_words` (0.53%), and `bn_mul_words` (0.52%).
`base64::...::internal_decode` is 0.56% and `serde_json` parsing leaves are below 0.5% each. This is direct evidence that
the B image is using AWS-LC's specialized big-integer routines, not the control arm's pure-Rust bigint loop.

This is a CPU profile of the full HTTP request path, so kernel networking and scheduler samples are intentionally present;
it is not a microbenchmark of bare RSA. It supports selecting AWS-LC over a custom SIMD/IPP/GPU rewrite, but does not justify
claiming a precise inclusive RSA percentage from this sampled (rather than Callgrind) run.
