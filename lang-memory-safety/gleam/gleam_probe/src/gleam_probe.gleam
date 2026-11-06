import gleam/int
import gleam/io
import gleam/list

pub fn main() {
  // OOB: list.at returns a Result, forcing the out-of-range case to be handled.
  let buf = [1, 2, 3, 4]
  case list.at(buf, 10) {
    Ok(value) -> io.println("value=" <> int.to_string(value))
    Error(_) -> io.println("value=OOB-REJECTED-AT-TYPE-LEVEL")
  }

  // UAF: safe Gleam has no manual free or raw pointer.
  io.println("uaf=INEXPRESSIBLE-IN-SAFE-GLEAM-BEAM-GC")

  // RACE: BEAM processes do not share mutable memory by default.
  io.println("race=NO-SHARED-MUTABLE-STATE-BY-DEFAULT")
}
