# Nim's default memory management (ARC/ORC, Nim >= 2.0) is deterministic ref-counting.
# A `ref` cannot be dereferenced after its last owner goes out of scope -- the object is
# freed but Nim does not null the other live `ref` bindings automatically in all cases;
# this fixture tests whether a stale ref after an explicit `=destroy`/`reset` is caught.
type Node = ref object
  value: int

proc makeDangling(): Node =
  var n: Node = Node(value: 42)
  result = n
  reset(n) # explicitly drop local owner; `result` still points at freed storage if UAF exists

let dangling = makeDangling()
echo "value=", dangling.value # observe: crash, IndexDefect/NilAccessDefect, or silently wrong value
