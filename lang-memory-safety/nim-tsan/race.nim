import std/locks
var counter: int = 0
proc worker() =
  for i in 1..100_000:
    counter += 1

var threads: array[4, Thread[void]]
for i in 0..3:
  createThread(threads[i], worker)
for i in 0..3:
  joinThread(threads[i])
echo "counter = ", counter, " expected = 400000"
