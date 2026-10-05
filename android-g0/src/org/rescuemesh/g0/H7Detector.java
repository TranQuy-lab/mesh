package org.rescuemesh.g0;

/**
 * H7 — phát hiện "chìm / bị cuốn" (bản Java của research/h7/h7_detector.py).
 * Nguyên lý: chìm xuống nước => áp suất tăng ~0,981 hPa/cm; bị cuốn => IMU lộn xộn.
 * Hằng số là `TK` — hiệu chuẩn bằng bồn nước trên máy có barometer trước khi nêu.
 * push() nhận MỘT bước tổng hợp 1 s: áp suất hPa, |a| g trung bình, std gyro °/s.
 */
public final class H7Detector {
    static final float RISE_RATE_MIN_HPA_S = 2.0f;
    static final float CONFIRM_DPA = 15.0f;
    static final float CONFIRM_S = 3.0f;
    static final float CHURN_GYRO_STD = 80.0f;
    static final float RESET_DPA = 3.0f;
    static final float COOLDOWN_S = 30.0f;
    static final float WATER_HPA_PER_CM = 0.981f;

    public enum State { NORMAL, SUSPECT, ALARM }

    public State state = State.NORMAL;
    public float dpaVisible() { return dpa; }   // Δp hiện tại (hPa) — để log
    private float t = 0f;
    private float suspectSince = -1f;
    private float dpa;
    private float pRef = Float.NaN;
    private float lastAlarmT = -1e9f;

    public State push(float dt, float pHpa, float accelG, float gyroStd) {
        t += dt;
        if (Float.isNaN(pRef)) {
            pRef = pHpa;
            return state;
        }
        if (state == State.NORMAL) {
            float rate = (pHpa - pRef) / dt;
            if (rate >= RISE_RATE_MIN_HPA_S && gyroStd >= CHURN_GYRO_STD) {
                state = State.SUSPECT;
                suspectSince = t;
                dpa = pHpa - pRef;
            } else {
                pRef = pHpa;
            }
            return state;
        }
        if (state == State.SUSPECT) {
            dpa = pHpa - pRef;
            boolean churnOk = gyroStd >= CHURN_GYRO_STD * 0.5f;
            boolean deepOk = dpa >= CONFIRM_DPA;
            boolean longOk = (t - suspectSince) >= CONFIRM_S;
            boolean fellBack = pHpa <= pRef + RESET_DPA;
            if (deepOk && longOk && churnOk) {
                state = State.ALARM;
                lastAlarmT = t;
                return state;
            }
            if (fellBack || (!churnOk && dpa < CONFIRM_DPA * 0.5f)) {
                state = State.NORMAL;
                pRef = pHpa;
            }
            return state;
        }
        // ALARM
        if (pHpa <= pRef + RESET_DPA && (t - lastAlarmT) >= COOLDOWN_S) {
            state = State.NORMAL;
            pRef = pHpa;
        }
        return state;
    }
}
