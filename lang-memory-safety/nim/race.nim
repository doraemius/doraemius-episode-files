import std/threadpool

var counter {.threadvar.}: int
var shared: ptr int

proc bump() =
  for j in 0 ..< 100_000:
    shared[] += 1 # unsynchronized shared pointer -- data race

proc main() =
  shared = cast[ptr int](alloc0(sizeof(int)))
  for i in 0 ..< 4:
    spawn bump()
  sync()
  echo "counter=", shared[]

main()
