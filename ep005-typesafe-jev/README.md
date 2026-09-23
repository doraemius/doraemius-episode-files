# EP005: TypeSafe's Jev AI model, self-hosted

Runs the video's three test inputs against [jeff](https://github.com/logan-markewich/jeff),
the MIT-licensed open reproduction of Jev's API, on your own GPU.

**Needs:** Linux with an NVIDIA GPU, `git`, `curl` and `jq`. The script installs
[uv](https://astral.sh/uv), clones jeff and starts it on `localhost:8010` with the local dev
key `devkey`.

```bash
cd ep005-typesafe-jev
./run-tests.sh
```

| File | What it asks |
|---|---|
| `support_query.json` | route a support ticket: department, frustration, urgency |
| `charmin_query.json` | will Costco raise the shelf price of Charmin next quarter, and by how much |
| `fomc_query.json` | the Oct 28, 2026 FOMC decision, given market pricing as of Sept 20-21, 2026 |

The Costco and FOMC inputs are a model's output on public text, shown to test the model.
They are not a forecast to trade on, and not financial advice.
