# Memory Safety: Rust vs Go vs Java vs Nim vs Gleam

These are the exact harmless fixtures used in the Doraemius memory-safety video. They compare
five languages on three narrow questions:

1. What happens on an out-of-bounds read?
2. Can safe/default code keep using an object after its lifetime ends?
3. What happens when four workers update one shared counter without synchronization?

This is **not** a general security ranking. It does not test injection, authentication,
configuration, compromised dependencies, unsafe extensions, native interfaces, or every possible
concurrency bug. A race detector can only report a race on a code path that actually runs.

## Run the comparison

You need Docker. The first run downloads the pinned toolchain images and Gleam's standard-library
dependency.

```console
python3 run.py
```

Run one language or the optional detector passes:

```console
python3 run.py go
python3 run.py rust
python3 run.py detectors
```

Available selections are `rust`, `go`, `java`, `nim`, `gleam`, `detectors`, and `all`.
The runner continues after expected compiler errors, panics, and exceptions because those outcomes
are part of the comparison. Default data-race counts vary from run to run; a correct-looking count
does not prove the program is race-free.

Pinned images:

- Rust: `rust:1-bookworm`
- Go: `golang:1.24-bookworm`
- Java: `eclipse-temurin:21-jdk`
- Nim: `nimlang/nim:2.2.0`
- Gleam: `ghcr.io/gleam-lang/gleam:v1.19.2-erlang-alpine`

## What the measured run found

The expected counter is `400000`: four workers times 100,000 increments.

| Language | Out-of-bounds read | Lifetime / UAF analogue | Unsynchronized counter, default build |
|---|---|---|---|
| Rust | Runtime panic | Compile-time rejection | Compile-time rejection |
| Go | Runtime panic | No classic dangling pointer under GC | Can finish silently with a wrong count |
| Java | Bounds exception | No classic dangling pointer under GC | Can finish silently with a wrong count |
| Nim | `IndexDefect` | ORC keeps the returned reference alive | Can finish silently with a wrong count |
| Gleam | `list.at` returns `Result` | No raw free in safe Gleam | No shared mutable memory between BEAM processes by default |

The recorded production run printed `292921` for Go, `136041` for Java, and `118189` for
Nim, each against `400000` expected and each with a clean default-build exit. Those exact numbers
are observations, not guaranteed outputs.

Two opt-in detector reruns were also measured:

- Go's `-race` build reported two data races.
- Nim through Clang ThreadSanitizer reported one data race. This pass is host-sensitive and may fail
  on Linux hosts whose address-space layout conflicts with TSan; the runner reports that limitation
  instead of changing host settings.

Java remains **not tested with a comparable runtime detector**. The OpenJDK Java ThreadSanitizer
proposal is still a draft, so this package does not substitute a paid or static-analysis tool and
pretend it is the same experiment.

## Sources and interpretation

- [Rust unsafe boundary](https://doc.rust-lang.org/stable/reference/unsafety.html)
- [Go data race detector and its coverage caveat](https://go.dev/doc/articles/race_detector)
- [Nim ARC/ORC memory management](https://nim-lang.org/docs/mm.html)
- [Erlang concurrency model](https://www.erlang.org/doc/system/conc_prog.html)
- [Draft OpenJDK Java ThreadSanitizer JEP](https://openjdk.org/jeps/8208520)

All fixture code in this folder is MIT-licensed under the repository's root `LICENSE`.
