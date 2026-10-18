# 5 Languages Tested: Which Fits Your HTTP + OAuth API Per Core?

Source documents for the Doraemius video of the same name. One physical core (two hardware threads), a 256 MiB limit, one reusable RS256 token, and a fixed-rate load generator: Rust, Go, Java, Nim and Gleam, each checked against the same 37-row conformance suite. This is a selection guide for a measured constraint on one box, not a language ranking.

## What's here

| file | what it is |
|---|---|
| `SCRIPT-DRAFT-2026-10-17.md` | the narration script and scope, one section per scene |
| `REPEATS-MEDIANS-2026-10-17.md` | the three-run medians behind the headline numbers |
| `PANEL-PROFILE-RUST-AUTH.md` | where the Rust CPU went (callgrind) and the limits of that profile |
| `NIM-GLEAM-OAUTH-OPTIMIZATION.md` | the Nim and Gleam OAuth builds and the forged-token finding |
| `MISS-WRITE-RESULTS-2026-10-17.md` | cache-miss and write medians, and the corrected downstream stub |
| `VIDEO-CONTENT-LOG-2026-10-17.md` | every finding with its evidence path, including the retractions |

## How to read them

- The documents were written as working notes. File paths inside them (for example `eval/...` or `profile/...`) point into the full working tree, which is not published here; the numbers and the reasoning are in the documents themselves.
- Tuned builds (Rust with `aws_lc_rs`, Nim's and Gleam's libcrypto builds) are pre-registered one-change variants, labelled as such everywhere. They are not extra contestants.
- Three findings were retracted during the work and are marked as retractions in the log: an "85k load-generator ceiling", a Go write failure, and a Java virtual-thread write gain. All three came from the test rig, not the languages.
- Qwen3-Coder helped, but did not independently write five finished services: it supplied the Go HTTP and OAuth first drafts; Rust is the control program; Nim and Gleam were rewritten with help; Java was built independently. The provenance table is in the script.

## What this does not say

One host, one physical core, repeated RSA-2048 verification of one reusable token, two generator threads, 128 connections, three-run medians at sustained steps only. Not measured: developer time, ecosystem, fault tolerance, other algorithms, other hardware.
