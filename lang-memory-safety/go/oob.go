package main

import (
	"fmt"
	"os"
	"strconv"
)

func main() {
	buf := [4]byte{1, 2, 3, 4}
	idx, _ := strconv.Atoi(os.Args[1])
	fmt.Println("value=", buf[idx]) // idx=10 -> runtime panic expected
}
