#!/usr/bin/env python3
"""SessionStart hook — re-inject the "Working Principles" section of the project CLAUDE.md.

Fires when a session starts or resumes (including after compaction). Prints the
Working Principles section (and only that section) to stdout, which Claude Code
surfaces as a system reminder. This counters the "agent forgot the rules after
compaction" failure mode without bloating CLAUDE.md.

Self-contained: stdlib only. Locates the project CLAUDE.md by walking UP from
`$CLAUDE_PROJECT_DIR` (or the cwd) to the first CLAUDE.md that actually contains a
Working Principles section — a session started in a subdirectory otherwise reinjected
nothing at all, silently, because a nested CLAUDE.md shadowed the repo-root one.
"""
import os
import sys
from pathlib import Path


def extract_working_principles(text: str) -> str:
    """Extract the "## Working Principles" section (until the next H2 heading)."""
    lines = text.splitlines()
    out: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.lstrip()
        if not in_section:
            if stripped.startswith("## ") and "Working Principles" in stripped:
                in_section = True
                out.append(line)
            continue
        # in_section
        if stripped.startswith("## "):
            break
        out.append(line)
    return "\n".join(out).rstrip()


def find_section() -> str:
    """Walk up from the project dir (or cwd) to the first CLAUDE.md that has the section.

    Stops at $HOME or the filesystem root. A nested CLAUDE.md without a Working
    Principles section is skipped rather than treated as the answer.
    """
    start = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    stop = Path.home()
    for d in (start, *start.parents):
        # Rules often move out of CLAUDE.md into a shared RULES.md and leave CLAUDE.md as a pointer; look in both.
        for name in ("CLAUDE.md", "RULES.md"):
            candidate = d / name
            if not candidate.is_file():
                continue
            try:
                section = extract_working_principles(
                    candidate.read_text(encoding="utf-8", errors="replace")
                )
            except OSError:
                section = ""  # never break the session over a hook
            if section:
                return section
        if d == stop:
            break
    return ""


def main() -> int:
    section = find_section()
    if section:
        print(section)
    else:
        # The failure mode is silence: after a refactor the section moves and the hook prints nothing. Warn in-context instead.
        print("WARNING: session-start-reinject found no '## Working Principles' section in any CLAUDE.md/RULES.md; rules were NOT re-injected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
