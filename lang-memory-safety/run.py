#!/usr/bin/env python3
"""Run the harmless five-language memory-safety fixtures in pinned Docker images."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Probe:
    heading: str
    image: str
    command: str


PROBES = {
    "rust": [
        Probe("Rust: out-of-bounds read (runtime rejection)", "rust:1-bookworm", "rustc rust/oob.rs -o /tmp/oob && /tmp/oob 10"),
        Probe("Rust: use-after-lifetime (compile rejection)", "rust:1-bookworm", "rustc rust/uaf.rs -o /tmp/uaf"),
        Probe("Rust: shared mutable race (compile rejection)", "rust:1-bookworm", "rustc rust/race.rs -o /tmp/race"),
    ],
    "go": [
        Probe("Go: out-of-bounds read (runtime rejection)", "golang:1.24-bookworm", "go run go/oob.go 10"),
        Probe("Go: GC/lifetime analogue", "golang:1.24-bookworm", "go run go/uaf.go"),
        Probe("Go: unsynchronized counter, default build", "golang:1.24-bookworm", "go run go/race.go"),
    ],
    "java": [
        Probe("Java: out-of-bounds read (runtime rejection)", "eclipse-temurin:21-jdk", "javac -d /tmp java/Oob.java && java -cp /tmp Oob 10"),
        Probe("Java: GC/lifetime analogue", "eclipse-temurin:21-jdk", "javac -d /tmp java/Uaf.java && java -cp /tmp Uaf"),
        Probe("Java: unsynchronized counter, default build", "eclipse-temurin:21-jdk", "javac -d /tmp java/Race.java && java -cp /tmp Race"),
    ],
    "nim": [
        Probe("Nim: out-of-bounds read (runtime rejection)", "nimlang/nim:2.2.0", "nim c --hints:off -o:/tmp/oob nim/oob.nim && /tmp/oob 10"),
        Probe("Nim: ORC/lifetime analogue", "nimlang/nim:2.2.0", "nim c --hints:off --mm:orc -o:/tmp/uaf nim/uaf.nim && /tmp/uaf"),
        Probe("Nim: unsynchronized counter, default build", "nimlang/nim:2.2.0", "nim c --hints:off --threads:on -o:/tmp/race nim/race.nim && /tmp/race"),
    ],
    "gleam": [
        Probe("Gleam: safe defaults for all three cases", "ghcr.io/gleam-lang/gleam:v1.19.2-erlang-alpine", "cd gleam/gleam_probe && gleam run"),
    ],
    "detectors": [
        Probe("Go: opt-in race detector", "golang:1.24-bookworm", "go run -race go/race.go"),
        Probe(
            "Nim: opt-in Clang ThreadSanitizer (host-sensitive)",
            "nimlang/nim:2.2.0",
            "nim c --cc:clang --threads:on --passC:-fsanitize=thread --passL:-fsanitize=thread --hints:off -o:/tmp/race-tsan nim-tsan/race.nim && /tmp/race-tsan",
        ),
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "selection",
        nargs="?",
        default="all",
        choices=[*PROBES, "all"],
        help="fixture group to run (default: all)",
    )
    return parser.parse_args()


def run_probe(probe: Probe) -> int:
    print(f"\n{'=' * 78}\n{probe.heading}\nimage: {probe.image}\n{'=' * 78}", flush=True)
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{ROOT}:/work",
        "-w",
        "/work",
        probe.image,
        "sh",
        "-lc",
        probe.command,
    ]
    completed = subprocess.run(command, check=False)
    print(f"[container exit {completed.returncode}]", flush=True)
    return completed.returncode


def main() -> int:
    args = parse_args()
    if shutil.which("docker") is None:
        print("error: Docker is not installed or not on PATH", file=sys.stderr)
        return 2

    groups = list(PROBES) if args.selection == "all" else [args.selection]
    for group in groups:
        for probe in PROBES[group]:
            run_probe(probe)

    print(
        "\nFinished. Non-zero container exits above are expected for compiler/runtime "
        "rejections. Compare the output with README.md; race counts are nondeterministic."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
