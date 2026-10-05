package org.rescuemesh.g0;

/**
 * Self-test hai detector mới (chạy JVM thuần, không cần Android):
 *  - FallDetector: rơi tự do → va đập → bất động => FALL_SUSPECTED; đi bộ => NONE.
 *  - H7Detector: chìm => ALARM; đi bộ/thang máy => NORMAL (khớp kịch bản Python).
 */
public final class DetectorSelfTest {
    private static int passed = 0, failed = 0;

    public static void main(String[] args) {
        testFallDetected();
        testWalkingNoFall();
        testH7SinkAlarm();
        testH7WalkNormal();
        testH7ElevatorNormal();
        testSosRecordRoundTrip();
        System.out.println("passed=" + passed + ",failed=" + failed);
        if (failed > 0) System.exit(1);
    }

    // --- FallDetector --------------------------------------------------------

    private static void testFallDetected() {
        FallDetector d = new FallDetector();
        boolean alarmed = false;
        // 0.6 s rơi tự do (~0 g) → đập 3.5 g → 1.5 s nằm yên (1 g)
        for (int i = 0; i < 12; i++) alarmed |= push(d, 0.05f, 0.05f, 0.05f);
        alarmed |= push(d, 0f, 0f, 3.5f);
        for (int i = 0; i < 40; i++) alarmed |= push(d, 0f, 0f, 1f);
        check("fall detected", alarmed);
    }

    private static void testWalkingNoFall() {
        FallDetector d = new FallDetector();
        boolean alarmed = false;
        for (int i = 0; i < 600; i++) {
            float s = (float) Math.sin(2 * Math.PI * 1.5 * i / 20.0);
            alarmed |= push(d, 0.1f * s, 0.05f, 1f + 0.2f * Math.abs(s));
        }
        check("walking no false alarm", !alarmed);
    }

    private static boolean push(FallDetector d, float x, float y, float z) {
        return d.push(x, y, z) == FallDetector.Event.FALL_SUSPECTED;
    }

    // --- H7Detector (cùng kịch bản research/h7/test_h7_detector.py) ----------

    private static void testH7SinkAlarm() {
        H7Detector d = new H7Detector();
        H7Detector.State end = H7Detector.State.NORMAL;
        // bắt đầu chìm giây 5, 30 cm/s (~29,4 hPa/s), lộn trong nước
        for (int i = 0; i < 25; i++) {
            float p = i < 5 ? 1013.25f : 1013.25f + 29.4f * (i - 4);
            float gyro = i < 5 ? 8f : 200f;
            end = d.push(1f, p + jitter(i), 1.3f, gyro);
        }
        check("h7 sink alarm", end == H7Detector.State.ALARM);
    }

    private static void testH7WalkNormal() {
        H7Detector d = new H7Detector();
        H7Detector.State end = H7Detector.State.NORMAL;
        for (int i = 0; i < 60; i++) {
            end = d.push(1f, 1013.25f + 0.4f * ((i % 3) - 1), 1.15f, 45f);
        }
        check("h7 walk normal", end == H7Detector.State.NORMAL);
    }

    private static void testH7ElevatorNormal() {
        H7Detector d = new H7Detector();
        H7Detector.State end = H7Detector.State.NORMAL;
        for (int i = 0; i < 40; i++) {
            float p = i < 10 ? 1101.25f - 8.8f * i : 1013.25f;
            end = d.push(1f, p, 1.0f, 8f);   // Δp lớn nhưng gyro yên
        }
        check("h7 elevator normal", end == H7Detector.State.NORMAL);
    }

    private static float jitter(int i) {
        return (float) Math.sin(i * 1.7) * 0.4f;
    }

    // --- SosRecord -----------------------------------------------------------

    private static void testSosRecordRoundTrip() {
        byte[] key = "device-key-for-tests".getBytes(java.nio.charset.StandardCharsets.UTF_8);
        byte[] frame = SosCodec.packSos(0x89abcdefL, 12345, 21.028511, 105.804817,
                1, 2, 3, 11, 3, 0, 7, 15, 42, key);
        SosRecord r = SosRecord.unpack(frame);
        boolean ok = r != null
                && Math.abs(r.lat - 21.028511) < 0.001
                && Math.abs(r.lon - 105.804817) < 0.001
                && r.srcId == 0x89abcdefL && r.seq == 42 && r.hop == 7 && r.ttl == 15;
        check("sos record round trip", ok);
    }

    private static void check(String name, boolean ok) {
        if (ok) { passed++; System.out.println("OK   " + name); }
        else { failed++; System.out.println("FAIL " + name); }
    }
}
