// Unsynchronized shared mutable state across threads -- safe Rust rejects this at
// compile time (no Sync/Send path for a raw shared &mut) unless the programmer opts
// into unsafe or an atomic/Mutex. This demonstrates the rejection.
use std::thread;

fn main() {
    let mut counter = 0i64;
    let r = &mut counter; // &mut captured by multiple threads below -- compile error expected
    let mut handles = vec![];
    for _ in 0..4 {
        handles.push(thread::spawn(move || {
            for _ in 0..100_000 {
                *r += 1;
            }
        }));
    }
    for h in handles { h.join().unwrap(); }
    println!("counter={}", counter);
}
