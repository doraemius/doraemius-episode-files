# H. Stale audit — before any handoff, outline or summary

Use before writing a handoff note, a script outline, a status summary or a plan after results have come in.

```text
Before you hand off or finalize, audit this document against the newest results.
1. List every line that says something is running, pending, unmeasured, planned, or "still to do".
2. For each, check whether the result or file now exists; fix the line or mark why it stays.
3. List claims that name a count, a number or a date and re-check them against the latest data.
Report what you changed. Then confirm nothing in the document contradicts the newest result files.
```

A tiny version you can run yourself: `grep -n -i -E "running|pending|unmeasured|to capture|todo|placeholder|planned" YOUR-DOC.md`, then check each hit against what exists now.
