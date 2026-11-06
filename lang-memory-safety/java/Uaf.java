import java.lang.ref.WeakReference;

// Java is GC'd; there is no freed-but-reachable heap object. Closest analogue: a
// WeakReference to an object that has already been collected -- Java requires a
// null-check, it cannot dereference a dangling pointer the way C can.
public class Uaf {
    public static void main(String[] args) {
        Object obj = new byte[1024 * 1024];
        WeakReference<Object> weak = new WeakReference<>(obj);
        obj = null;
        System.gc();
        Object got = weak.get(); // null if collected -- safe either way, no dangling deref possible
        System.out.println("got=" + got);
    }
}
