public class Race {
    static int counter = 0;
    public static void main(String[] args) throws InterruptedException {
        Thread[] ts = new Thread[4];
        for (int i = 0; i < 4; i++) {
            ts[i] = new Thread(() -> {
                for (int j = 0; j < 100000; j++) counter++; // unsynchronized -- data race
            });
            ts[i].start();
        }
        for (Thread t : ts) t.join();
        System.out.println("counter=" + counter);
    }
}
