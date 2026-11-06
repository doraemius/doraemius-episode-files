package main

import (
	"fmt"
	"sync"
)

func main() {
	counter := 0
	var wg sync.WaitGroup
	for i := 0; i < 4; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 100000; j++ {
				counter++ // unsynchronized -- data race
			}
		}()
	}
	wg.Wait()
	fmt.Println("counter=", counter)
}
