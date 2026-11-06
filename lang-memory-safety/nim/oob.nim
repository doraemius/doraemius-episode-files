import os, strutils

let buf = [1'u8, 2, 3, 4]
let idx = parseInt(paramStr(1))
echo "value=", buf[idx] # idx=10 -> IndexDefect expected (release: bound checks still on by default)
