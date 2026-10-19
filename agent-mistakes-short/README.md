# Agent mistakes come in kinds — one-step checks you can paste

Companion files for the Doraemius Short "22 AI Agent Mistakes in 8 Kinds". Everything here is plain text you can paste into your own agent setup.

**What this is.** I went through ten days of my own coding-agent session logs and counted 22 times the agent was wrong (one person, one setup, my own classification). They fit into eight kinds. For 16 of the 22, the evidence that would have caught the mistake was already available at the moment it was made, or one cheap step away.

**What did not work.** A cheap alarm ("flag any answer that states a number with no source") flagged 3 of 13 bad answers, about as often as it flagged normal ones (20%). Most bad answers already cited something. A citation is not a check. Neither was watching context size or turn count.

**What did work.** Re-reading the source and comparing. Each kind of mistake has its own one-step version of that:

| Kind (count) | One-step check | Prompt |
|---|---|---|
| A. Guess or prediction stated as a result (4) | Write the prediction down before measuring, compare when the result lands | [`A-prediction-ledger.md`](prompts/A-prediction-ledger.md) |
| B. Old or secondhand source trusted (4) | Open the live source, quote the line | [`B-live-source.md`](prompts/B-live-source.md) |
| C. Premise or arithmetic not checked (4) | Recompute from the raw inputs | [`C-recompute.md`](prompts/C-recompute.md) |
| D. World state assumed, not queried (2) | Run the one command that shows it | [`D-query-state.md`](prompts/D-query-state.md) |
| E. Label or status overstated the result (3) | Compare the label with the record's own definition | [`E-label-vs-definition.md`](prompts/E-label-vs-definition.md) |
| F. Misread or over-extended the ask (3) | Restate the ask next to the exact words, list what you will not build | [`F-restate-the-ask.md`](prompts/F-restate-the-ask.md) |
| G. Flaw found only by probing (1) | One adversarial probe before "done" | [`G-one-probe.md`](prompts/G-one-probe.md) |
| H. Notes left stale after new results (1) | Grep the document for statements newer results overturned | [`H-stale-audit.md`](prompts/H-stale-audit.md) |

There is also a one-paste version of all eight: [`all-in-one.md`](prompts/all-in-one.md), and a small session-start hook that re-injects your rules and **warns loudly if it finds nothing to inject**: [`hooks/`](hooks).

## How far to trust this

- One operator, ten days, one classification by one labeller. No second reviewer.
- These checks are the ones that caught the mistakes after the fact, or that were applied when the agent verified. Applying them earlier is inferred, **not measured**. I have not tested these prompts as prompts, and I have not shown that they prevent mistakes.
- Kind A (predictions) cannot be caught early by a check, because the data does not exist yet. The prompt only makes sure a prediction cannot quietly become a finding.
- Timing: for the 14 mistakes where both ends are known, a typical one stood for about 22 assistant turns (range 2 to 74) before it was caught.

## Credits and licence

Prompts and hook: [MIT](../LICENSE), like the rest of this repo. Video music: "Back Fire" by RockCapers via OpenTracks (not included here). Voice: Kokoro-82M, voice am_puck. Lettering: Anton (SIL Open Font License).
