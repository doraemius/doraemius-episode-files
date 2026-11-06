fn main() {
    let buf = [1u8, 2, 3, 4];
    let idx = std::env::args().nth(1).unwrap().parse::<usize>().unwrap();
    println!("value={}", buf[idx]); // idx=10 -> out of bounds
}
