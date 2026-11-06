public class Oob {
    public static void main(String[] args) {
        byte[] buf = {1, 2, 3, 4};
        int idx = Integer.parseInt(args[0]);
        System.out.println("value=" + buf[idx]); // idx=10 -> ArrayIndexOutOfBoundsException expected
    }
}
