# Session-start rules re-injection hook (with a loud failure mode)

`session-start-reinject.py` prints the `## Working Principles` section of your project rules file at session start, resume and after compaction, so the agent sees your rules again.

The important part is the failure mode: if it cannot find the section (you moved the rules to another file, renamed the heading), it **prints a warning into the session** instead of printing nothing. A hook that silently outputs zero bytes looks identical to a hook that works.

Install (Claude Code `settings.json`, project level):

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "*", "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/session-start-reinject.py\"", "timeout": 5 } ] }
    ]
  }
}
```

Test it before you trust it: run it by hand from your project root and from a subdirectory, and confirm the byte count is not zero.

```bash
CLAUDE_PROJECT_DIR="$PWD" python3 .claude/hooks/session-start-reinject.py | wc -c
```

It looks for the heading in `CLAUDE.md` first, then `RULES.md`, walking up from the project directory. Standard library only. Not shown here: that re-injecting rules changes how often the agent follows them.
