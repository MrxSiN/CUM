public final class Runner {
    public static void main(String[] args) {
        int left = Integer.parseInt(args[0]);
        int right = Integer.parseInt(args[1]);
        System.out.print(Arithmetic.combine(left, right));
    }
}
