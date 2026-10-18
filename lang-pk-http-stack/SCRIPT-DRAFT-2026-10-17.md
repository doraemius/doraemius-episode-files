# Script draft — five languages, HTTP and OAuth

Status: the narration script this video was voiced from (the draft text; the video follows it).

Proposed title: **5 Languages: Which Fits Your API Per Core? HTTP + OAuth**

Audience: a backend engineer choosing an implementation for a read-heavy API who needs a measured, narrow answer rather than a general language ranking. The answer is a best fit for a stated constraint **on this box**, not a winner.

Scope spoken in this script: repeated RS256 JWT verification of one reusable token plus a cached read, on one physical core exposed as two logical CPUs, with a 256 MiB container limit. The diagnostic no-token-check copies are not production OAuth cost. Miss and write results use the same box and OAuth, but a different request path.

## 00:00–00:12 — Cold open — F1

### Spoken narration

{H} One JWT check took this Rust API from sixty thousand requests a second to five thousand on the same service and box, then one crypto setting brought it back to twenty thousand. So which of five languages is the best fit for your API per core, and how did our test rig create two false stack stories before we caught it?

### Visual / cue notes

F1. Show the no-token-check diagnostic bar first, then drag the finger to the as-built Rust OAuth bar. Count up the `-92%` after both values have been seen. Small scope line: “cached read · repeated RS256 verify · 1 physical core”.

Source: `REPEATS-MEDIANS-2026-10-17.md` (Rust no-OAuth and OAuth medians); `PANEL-AUTH-TUNING.md` (Rust B).

## 00:12–01:42 — What was actually built — F2

### Spoken narration

Before the chart avalanche, here is the honest version of the local-AI part: Qwen3-Coder helped, but it did not write five finished services by itself.

For Go, it wrote the first HTTP and OAuth drafts in two staged steps, then we fixed thirty-three defects by hand while Claude wrote the WebSocket, gRPC, and telemetry pieces.

Rust is the control program, because Qwen’s Rust attempt was replaced rather than repaired instead of becoming the measured implementation.

Nim, with its Nimble package manager, and Gleam were rewritten with help after its attempts stopped, while Java came from an independent coding-agent session.

That is not a purity test but provenance, because you deserve to know whether I am showing you a model draft, a repaired program, or a separate control.

The tuned builds need the same warning: Rust's alternate crypto backend, Nim's tuned build, and Gleam's tuned build were pre-registered one-change variants written by Claude, with their exact labels on screen.

They are evidence about named changes rather than extra contestants Qwen wrote, so the question remains which implementation fits a measured constraint on this one box.

Local AI is part of how the work happened and part of the lesson, but it is not a claim that one model settled a five-language contest.

### Visual / cue notes

F2. Reveal one provenance row at a time. Ring “Qwen3-Coder first drafts” in Go, then underline “control program” in Rust. Hold the tuned-build row last while the qualification is spoken.

Source: `SCRIPT-OUTLINE-DRAFT-2026-10-17.md` provenance table; `go-staged/BUG-LEDGER.md`; `rust-staged/QWEN-RUST-FINDINGS.md`; `SCORED-CLOSEOUT-2026-10-16.md`; [Nim features — Nimble is Nim’s package manager](https://nim-lang.org/features.html).

## 01:42–02:30 — Rules before results — F3

### Spoken narration

Here are the rules I locked before looking for a favorite: every stack passes the same thirty-seven-row contract on two logical CPUs, one physical core, and a 256 MiB limit.

The generator keeps offering work at a fixed rate instead of politely slowing down when a server struggles, which lets the chart show where each implementation reaches its knee.

I call a step sustained only when the median reaches at least ninety-seven percent of the offered rate and median p50 stays below five milliseconds, using fresh-process three-run medians for headlines.

The coarser load ladder tells us where the wall is rather than a magical exact ceiling, while HAProxy is a TCP pass-through yardstick that keeps the scale visible without crowning an application server.

And one important translation: I use “OAuth” for familiar API-auth context, but the measured hot path is repeated RS256 JWT verification of one reusable token.

It does not measure issuance, refresh, rotation, remote introspection, or a busy identity provider, so those remain the next test rather than a hidden implication of this one.

### Visual / cue notes

F3. Reveal one rule every four seconds. End on a persistent scope footer: “37 tests · 2 logical CPUs = 1 core · 256 MiB · repeated RS256 verify”.

Source: `REPEATS-MEDIANS-2026-10-17.md`; `SAMPLED-COMPARISON.md`; `PANEL-AUTH-TUNING.md`.

## 02:30–04:00 — Round one: HTTP with token validation bypassed — F4–F6

### Spoken narration

First, take the token check out, not because production has no authentication, but because this diagnostic copy shows what the web stack can do when repeated signature verification is absent.

The useful shape is the knee: latency stays low while the service has room, then a small rate increase becomes a wall.

That is why the last step that keeps up matters more than a tool’s biggest number, which can arrive after useful service has already disappeared.

On this diagnostic path, Java sustains eighty thousand requests a second, while Rust is about sixty thousand although one of three runs is just under the sustained bar.

Go’s thinner HTTP-only arm also sustains sixty thousand, so the chart places that result beside the full service rather than silently treating them as the same build.

Nim sustains forty-five thousand and Gleam ten thousand, but these are not five general-purpose speed rankings because the copies are diagnostic and Go’s HTTP-only arm is thinner than its full service.

Java’s result here is one Vert.x event loop in one server instance, with one event-loop thread doing the request work.

The spread still shows how much cached HTTP several implementations move before repeated RSA verification enters the picture, which is the diagnostic purpose of this section.

At their own sustained diagnostic steps, Rust, Go, and Nim sit roughly in the eight-to-eleven MiB range, while Gleam is about seventy-two MiB on the BEAM.

Java is around one hundred thirteen to one hundred twenty-one MiB on its JVM, which still fits the limit but leaves a visibly different amount of room.

So if a 256 MiB limit is keeping you awake, the measured best fit is Rust, Go, or Nim on this box.

That statement comes from their observed memory here, not from ecosystem or developer experience, because I did not measure either of those axes.

Java also reaches its no-token-check wall while using under one core on average, although its 100-millisecond peak reaches almost both logical CPUs.

Treat that as short-window, fresh-process behavior on this setup rather than a universal JVM verdict, because the test does not establish a general JVM ceiling.

The next panel asks a simpler question: at similar CPU use, how much throughput does each implementation turn into useful work before the knee arrives?

The efficiency panel then shows why the low-load region can mislead, since fixed request costs shrink per request only until the wall reverses that benefit.

### Visual / cue notes

F4: show full chart for one second; underline the low-latency band, then follow one line to its X. Repeat the wall cue stack-by-stack, without calling a winner. F5: focus Java, then Gleam, for their distinct CPU/throughput shapes. F6: follow one response-cost curve; keep exact labels visual, not narrated.

Sources: `REPEATS-MEDIANS-2026-10-17.md` (no-OAuth medians and memory); `SAMPLED-COMPARISON.md` (diagnostic scope and Java event-loop finding).

## 04:00–05:15 — Add repeated JWT verification — F7

### Spoken narration

Now put repeated RS256 verification back on every cached read: Rust as built falls from about sixty thousand to five thousand sustained requests a second.

Go’s full service falls from forty-five thousand to fifteen thousand, while Java moves from eighty thousand to twenty thousand under the same repeated-token test.

Nim’s cached-read tuned build reaches twenty thousand, while Gleam’s tuned build reaches ten thousand—the same step Gleam reached without the check.

That contrast reflects the verifier paths in these implementations rather than a language property, which is why the frame carries named-build badges instead of a winner label.

That first Rust drop is the opening clue rather than a language verdict, because subtracting the diagnostic copy from the authenticated service does not give you a universal OAuth tax.

It tells us that authentication dominates for this implementation and repeated-token workload, which is why a selection guide has to name the build rather than flatten every observation into “Rust.”

Rust as built and Rust with a different crypto backend are separate observations, while Nim and Gleam contain pre-registered changes.

Go and Java have one measured build each, so I will not turn unequal tuning into an overall ranking that pretends every row received the same treatment.

### Visual / cue notes

F7. Grouped bars. Finger descends each before/after pair. Keep a visual badge on tuned builds: “pre-registered variant”. Hold Java and Go as single-build observations.

Source: `REPEATS-MEDIANS-2026-10-17.md`; `NIM-GLEAM-OAUTH-OPTIMIZATION.md`.

## 05:15–07:25 — The Rust mechanism — F8–F9

### Spoken narration

For Rust, we can see where that work went: Callgrind puts ninety-two point six percent of the as-built control’s user-space instructions in RSA signature verification, not routing, caching, or vague “Rust overhead.”

That instruction share is not the hook’s ninety-two-percent throughput drop; one describes CPU instructions, while the other compares two different request paths in this measured implementation.

Then one feature flag swaps the backend to the `aws_lc_rs` build, moving the sustained step from five thousand to twenty thousand.

The median achieved rate moves from four thousand eight hundred fifty-five to nineteen thousand four hundred twenty-three, which is the measured fourfold recovery behind the opening claim.

At the same five-thousand offered rate, observed CPU falls from one point four one cores to zero point three six, a useful result that still does not make crypto libraries interchangeable or operationally free.

When authentication is in your hot path, look up which crypto backend your JWT library actually uses before comparing languages.

Nim’s cached-read tuned build also changes BearSSL verification and PEM decoding into refresh-time key parsing plus libcrypto verification, so it is not the same one-flag experiment as Rust.

That Nim build reaches twenty thousand, Gleam’s tuned build adds a native verifier and reaches ten thousand, Java reaches twenty thousand with stock JCA, and Go reaches fifteen thousand with its standard library.

The fair conclusion is not that libraries matter more than languages everywhere, because the experiments did not change every stack in the same way.

Changing the crypto or backend stack materially changed Rust, Nim, and Gleam results, making the default path part of the system you choose.

### Visual / cue notes

F8: underline the 92.6% row; arrow label “RSA verify.” F9: ring Rust’s seven-percent and twenty-nine-percent HAProxy-relative pair, then traverse that pair with the finger. Treat Nim and Gleam as named multi-change variants; ring Java’s stock JCA separately.

Sources: `PANEL-PROFILE-RUST-AUTH.md`; `REPEATS-MEDIANS-2026-10-17.md`; `NIM-GLEAM-OAUTH-OPTIMIZATION.md`; `PANEL-AUTH-TUNING.md`.

## 07:25–08:40 — OAuth resource fit — F10

### Spoken narration

Throughput alone still does not pick a stack for you: at their own sustained OAuth steps, tuned Rust, Go, and Java cluster around a three-and-a-half-millisecond median p99.

Nim’s cached-read tuned build is four point four seven, while tuned Gleam and Rust as built are both above ten milliseconds on their named cached-read builds.

Those values come from different rates and this tool resolves latency to roughly one millisecond, so the measured low-p99 group is tuned Rust, Go, and Java rather than a latency champion.

At the common five-thousand offered rate, the Rust backend change gives the clearest CPU contrast, using zero point three six cores instead of one point four one as built.

The full CPU row stays on screen because it is a single-run direction rather than a fine ranking, while Java’s displayed low CPU is also a named observation.

Memory gives a clearer operational limit: Rust is roughly eight MiB at its OAuth sustained steps, while Go is eleven to thirteen and Nim’s cached-read tuned build is eighteen to nineteen.

Gleam is about seventy-two MiB and Java about one hundred thirteen to one hundred twenty-one, giving each deployment a different margin beneath the same limit.

Java still fits under the 256 MiB cached-read cap, but its JVM was not heap-tuned in this comparison.

Its miss path later gets close to that cap, which matters for deployment on this box even though the cached-read result remains inside the limit.

At five thousand offered requests, Java shows the lowest observed CPU on the full row, while Gleam is already using both logical CPUs at its ten-thousand-request sustained step.

### Visual / cue notes

F10. Ring the three close p99 values together without ordering them. Then isolate the memory badges: native group, BEAM, JVM. Footnote stays visible: “own sustained rate; 3-run medians; Java short-window fresh process.”

Sources: `REPEATS-MEDIANS-2026-10-17.md`; `SAMPLED-COMPARISON.md`.

## 08:40–11:15 — Three checks that kept us honest — F11, F15, F12

### Spoken narration

Now for the part that should make you distrust a clean benchmark just enough, starting with how a profile can tell the truth while hiding the cost you need to see.

In Nim, telemetry looked like a five-percent increase in user-space instructions, but the measured addition was five hundred twenty-three microseconds of kernel time per request.

The exporter opened a connection per span inside the request, which is why its kernel cost escaped the user-space profile’s reassuring five-percent story.

Moving export off the request path and batching it removed that collapse, which is why user-space instruction totals alone were never enough to explain the observed throughput.

Second, all tests green is a claim about your tests: a faster Nim verifier passed the thirty-seven-row contract and still accepted a JWT signature spelled two ways.

The final base64url character could change without changing decoded bytes, a forged-token battery found it, and requiring canonical re-encoding fixed it without making Nim uniquely unsafe.

The lesson is that every faster verifier needs an adversarial battery as well as a happy-path contract, especially when its implementation changes a security-sensitive boundary.

Third, the test rig itself can manufacture a language bug: we initially blamed Go’s write failures on Go, while a Java virtual-thread change looked like a write improvement.

When a second probe disagreed, we found that the downstream performance stub closed keep-alive connections after POSTs because it ignored the POST body, which was a rig defect.

On the corrected stub, Go as built sustains ten thousand writes per second, while Java as built and the virtual-thread variant both sustain seven thousand five hundred, so those earlier findings are retracted.

That is a me bug. Twice. The lesson is not that benchmarks are useless; your stub, connection policy, and probes are part of the measurement, so a disagreeing instrument means you find the code before promoting a story.

### Visual / cue notes

F11: small user segment badge “+9%”; ring the 523-kernel segment and label “invisible to callgrind.” F15: freeze the non-canonical signature response, ring the unexpected success, arrow “same decoded bytes.” F12-three-paths or dedicated rig card: show “stub closes POST keep-alive” then strike through Go-502 and Java-J1 gain as retracted. Do not reuse the obsolete bug chart.

Sources: `NIM-GLEAM-OAUTH-OPTIMIZATION.md`; `VIDEO-CONTENT-LOG-2026-10-17.md` entries 44–45; `MISS-WRITE-RESULTS-2026-10-17.md` final/repeats sections.

## 11:15–14:00 — Three request paths, not one answer — F12-three-paths

### Spoken narration

The cached authenticated read is not the whole API, so the other paths are a cache miss that fetches downstream and a unique idempotent write that mutates downstream, both measured as three-run median sustained steps.

Rust with `aws_lc_rs` sustains fifteen thousand cache misses and ten thousand writes, while Go and Nim's final tuned build sustain ten thousand on both paths.

Java sustains seven thousand five hundred on both, Gleam's tuned build sustains three thousand on both, and Rust as built is around two to three thousand on misses with three thousand on writes.

Those values are named builds on one connection model and one downstream stub after its POST keep-alive defect was fixed, not a general five-language leaderboard.

The fixes still teach something useful: Nim starts with a new downstream TCP connection per request, which is waiting and connection churn rather than throughput work.

A persistent client fixes Nim’s miss path, but writes then sit at a forty-one-point-five-millisecond p50 with idle CPU because of Nagle plus delayed ACK, until `TCP_NODELAY` moves the write path to ten thousand.

That is a clean diagnostic pattern where idle CPU plus fixed rising latency can mean waiting rather than computation, so ask what the request is waiting for before asking which language is slow.

Java’s miss path reaches seven thousand five hundred while memory climbs to roughly two hundred thirty-eight to two hundred forty MiB, making headroom part of deployment under this 256 MiB container limit.

Gleam’s lower three-thousand figures do not license a pile-on, because this video measures only three request paths rather than BEAM fault tolerance, supervision, deployment tradeoffs, or developer productivity.

### Visual / cue notes

F12-three-paths. For each stack, cue cached read, then miss, then write. On Nim, ring the as-built low path, finger through the connection-reuse change, then ring the final `TCP_NODELAY` build. Java receives a memory badge, not an evaluative color. Keep all inactive stacks ice/grey.

Source: `MISS-WRITE-RESULTS-2026-10-17.md` (3-run repeat table and final corrected-write table).

## 14:00–15:45 — Pick by your measured constraint — F13, F16

### Spoken narration

So here is the answer I would actually use to choose: if your immediate constraint is low observed memory on authenticated cached reads under 256 MiB, look first at Rust, Go, or Nim.

Their observed figures are roughly eight, eleven to thirteen, and eighteen to nineteen MiB at their own sustained steps, which is the measured basis rather than a statement about ecosystem or developer experience.

If you want observed cached-read OAuth throughput without changing a crypto backend, Java reaches twenty thousand and Go fifteen thousand as built.

Those are the two as-built observations on this box; the frame shows their named builds and does not claim they are tied on every measured constraint.

If you are willing to use a pre-registered named variant, Rust with `aws_lc_rs`, Nim’s cached-read tuned build, and Java each reach twenty thousand authenticated cached reads here.

Go reaches fifteen thousand and Gleam’s tuned build ten thousand, while the visual keeps the exact build labels beside every value rather than speaking them as a string of version names.

The necessary follow-up is to check the maintenance, security, and deployment implications of that exact library choice in your system, because those are important axes I did not measure.

If your service is miss-heavy or write-heavy, do not choose from the cached-read chart alone, because the named builds move differently once every request reaches downstream.

Rust with `aws_lc_rs`, Go, and Nim’s final miss-and-write build reach ten thousand writes, while Rust reaches fifteen thousand misses and Go with Nim reach ten thousand.

Java’s observed seven-thousand-five-hundred miss and write steps come with a much tighter memory margin on misses, which makes that constraint visible before the service reaches the container limit.

Whatever language you choose, inspect the crypto backend, because it moved one measured Rust implementation fourfold and changed the measured Nim and Gleam paths; “uses JWT” is not enough information about a hot path.

My Monday checklist is short but concrete: look up the backend behind your JWT verifier, ramp until you find the knee, and split user from kernel CPU.

Then run forged-token cases, kill one key fetch, and test downstream connection behavior, because those checks catch failures that a happy-path throughput line cannot reveal.

### Visual / cue notes

F13. Underline one constraint row, then ring each cyan fitting-stack mark. No ordering animation among stacks with close results. F16 follows: reveal one checklist badge per sentence.

Sources: `REPEATS-MEDIANS-2026-10-17.md`; `MISS-WRITE-RESULTS-2026-10-17.md`; `NIM-GLEAM-OAUTH-OPTIMIZATION.md`; `SCRIPT-OUTLINE-DRAFT-2026-10-17.md` decision guide.

## 15:45–17:30 — Limits and close — F14 / end screen

### Spoken narration

Keep the limits attached to the advice: this is one host, one physical core, repeated RSA-2048 verification of one reusable token, two generator threads, one hundred twenty-eight connections, and three-run medians only at sustained steps.

CPU peaks are one-hundred-millisecond samples, CPU sets isolate eligibility rather than cache, memory bandwidth, power, or SMT effects, Java is short-window fresh-process behavior, and tuned builds are named variants rather than scored arms.

So the conclusion is deliberately smaller than “best language”: pick the best fit for the measured constraint you actually have on a box like this.

Then make crypto, connection behavior, and failure cases visible before they choose for you, because a clean benchmark hides exactly the problems this test had to uncover.

Next, I’ll run issuance, refresh, rotation, and algorithm choices under the same harness and rules, so subscribe if you want that result on the end screen.

### Visual / cue notes

F14. Underline each limit while it is spoken; retain the small workload footer. Last sentence over native end screen: one video, one subscribe.

Sources: `REPEATS-MEDIANS-2026-10-17.md`; `SAMPLED-COMPARISON.md`; `VIDEO-REVIEW-CODEX-2026-10-17.md`.

## Production checks before voice

- Spoken-word count must be recalculated after any edit. Target delivery: 15–20 minutes at the approved Michael/Puck starting pace, never over the 170-wpm hook cap.
- Every number spoken above appears in the cited episode evidence. Exact build labels remain visual where possible; visual notes are not narration input.
- Retractions are explicit: the 85k load-generator claim, Go write 502 claim, and Java J1 virtual-thread write gain are not presented as findings.
- Voice was synthesized only after script approval and a single listening sample.
