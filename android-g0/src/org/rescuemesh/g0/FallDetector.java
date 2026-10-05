package org.rescuemesh.g0;

/**
 * Tầng T1 — phát hiện ngã bằng 3 chữ ký từ gia tốc kế 20 Hz:
 * rơi tự do (~0 g) → va đập (≥2,5 g) → bất động (std thấp ~1–2 s).
 * Các ngưỡng là `TK` (đặt trước, chưa `ĐO` trên người thật — chờ drill);
 * tầng AI (RQ1, LOSO) sẽ nối thêm sau khi kernel cho model.
 */
public final class FallDetector {

    public enum Event { NONE, FALL_SUSPECTED }

    // `TK` — phải hiệu chuẩn bằng drill D-ngã trước khi tuyên bố hiệu năng
    static final float FREEFALL_G = 0.4f;        // |a| dưới ngưỡng này = rơi tự do
    static final int FREEFALL_MIN_SAMPLES = 3;   // ≥150 ms ở 20 Hz
    static final float IMPACT_G = 2.5f;          // va đập tối thiểu
    static final int IMPACT_WINDOW_SAMPLES = 12; // trong 600 ms sau rơi tự do
    static final int STILL_SAMPLES = 24;         // 1,2 s bất động sau va đập
    static final float STILL_STD_G = 0.12f;      // std |a| thấp = nằm yên

    private enum Phase { IDLE, FREEFALL, WAIT_IMPACT, STILL }
    private Phase phase = Phase.IDLE;
    private int phaseSamples;
    private final float[] stillWindow = new float[STILL_SAMPLES];
    private int stillCount;

    /** Nhận một mẫu gia tốc (đơn vị g) theo từng trục. Trả về sự kiện nếu có. */
    public Event push(float ax, float ay, float az) {
        float mag = (float) Math.sqrt(ax * ax + ay * ay + az * az);
        Event out = Event.NONE;
        switch (phase) {
            case IDLE:
                if (mag < FREEFALL_G) {
                    phase = Phase.FREEFALL;
                    phaseSamples = 1;
                }
                break;
            case FREEFALL:
                phaseSamples++;
                if (mag >= IMPACT_G) {
                    phase = Phase.STILL;
                    phaseSamples = 0;
                    stillCount = 0;
                } else if (mag > FREEFALL_G || phaseSamples > IMPACT_WINDOW_SAMPLES) {
                    // rơi tự do đủ dài nhưng chưa đập (bỏ tay máy) — quay lại IDLE
                    phase = Phase.IDLE;
                }
                break;
            case STILL:
                stillWindow[stillCount % STILL_SAMPLES] = mag;
                stillCount++;
                phaseSamples++;
                if (stillCount >= STILL_SAMPLES) {
                    if (std(stillWindow, Math.min(stillCount, STILL_SAMPLES)) < STILL_STD_G) {
                        reset();
                        out = Event.FALL_SUSPECTED;
                    } else if (phaseSamples > STILL_SAMPLES * 2) {
                        reset();
                    } else if (mag >= IMPACT_G) {
                        // va đập lần 2 (lăn tiếp) — kéo dài cửa sổ bất động
                        phaseSamples = 0;
                        stillCount = 0;
                    }
                }
                break;
            default:
                reset();
        }
        return out;
    }

    private static float std(float[] v, int n) {
        float mean = 0f;
        for (int i = 0; i < n; i++) mean += v[i];
        mean /= n;
        float acc = 0f;
        for (int i = 0; i < n; i++) {
            float d = v[i] - mean;
            acc += d * d;
        }
        return (float) Math.sqrt(acc / n);
    }

    private void reset() {
        phase = Phase.IDLE;
        phaseSamples = 0;
        stillCount = 0;
    }
}
