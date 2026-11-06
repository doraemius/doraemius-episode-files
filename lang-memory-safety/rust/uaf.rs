// Safe Rust cannot express a use-after-free the way C/C++ can -- the borrow checker
// rejects it at compile time. This file demonstrates that rejection (it will not compile).
fn main() {
    let r;
    {
        let x = Box::new(42);
        r = &x; // borrow of `x`
    } // `x` dropped here
    println!("{}", r); // use after `x` is gone -- compile error expected
}
