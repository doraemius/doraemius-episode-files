package main

import "fmt"

// Go is GC'd: there is no "freed" heap object to use after free in the C sense.
// The closest analogous defect is capturing a loop variable by reference and using
// it after the loop body's intended lifetime (pre-Go1.22 classic footgun). Observe
// whether it produces the "stale" value or the intended one.
func main() {
	fns := make([]func() int, 3)
	for i := 0; i < 3; i++ {
		fns[i] = func() int { return i } // captures `i` -- behavior changed Go 1.21->1.22
	}
	for _, f := range fns {
		fmt.Println(f())
	}
}
