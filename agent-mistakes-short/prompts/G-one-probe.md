# G. One probe — before "done" on a service, queue or parser

Use before declaring a component finished when a test suite is green.

```text
Before you say a component is done, run one adversarial probe the test suite does not cover: a stalled or slow client, empty input, ten times the size, a repeated request, a dependency that is down.
Report the probe and its result (memory, errors, time). If the probe finds a defect, add a test for it before you fix it.
Say explicitly which behaviours the existing tests never exercise.
```
