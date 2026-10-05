package org.rescuemesh.g0;

/** Hình học trắc địa tối thiểu: khoảng cách + hướng (bearing) giữa hai toạ độ. */
public final class Geo {
    private Geo() {}

    public static double distanceMeters(double lat1, double lon1, double lat2, double lon2) {
        double r = 6_371_000.0;
        double p1 = Math.toRadians(lat1), p2 = Math.toRadians(lat2);
        double dp = Math.toRadians(lat2 - lat1), dl = Math.toRadians(lon2 - lon1);
        double a = Math.sin(dp / 2) * Math.sin(dp / 2)
                + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) * Math.sin(dl / 2);
        return 2 * r * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }

    /** 0° = bắc, 90° = đông, theo chiều kim đồng hồ. */
    public static double bearingDegrees(double lat1, double lon1, double lat2, double lon2) {
        double p1 = Math.toRadians(lat1), p2 = Math.toRadians(lat2);
        double dl = Math.toRadians(lon2 - lon1);
        double y = Math.sin(dl) * Math.cos(p2);
        double x = Math.cos(p1) * Math.sin(p2) - Math.sin(p1) * Math.cos(p2) * Math.cos(dl);
        return (Math.toDegrees(Math.atan2(y, x)) + 360.0) % 360.0;
    }

    private static final String[] OCTANTS = {"B", "ĐB", "Đ", "ĐN", "N", "TN", "T", "TB"};
    private static final String[] ARROWS = {"\u25B2", "\u2197", "\u25B6", "\u2198",
                                            "\u25BC", "\u2199", "\u25C0", "\u2196"};

    /** Tên hướng 8 cung + mũi tên tương ứng. */
    public static String octant(double bearing) {
        int idx = (int) Math.round(bearing / 45.0) % 8;
        return OCTANTS[idx] + " " + ARROWS[idx];
    }
}
