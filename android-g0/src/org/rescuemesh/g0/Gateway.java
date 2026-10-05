package org.rescuemesh.g0;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Build;
import android.telephony.SmsManager;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * Cổng ra (khâu ③): đẩy hàng đợi SOS lên server khi có Internet, SMS dự phòng
 * khi chỉ còn sóng. Chạy trên luồng nền; mỗi lượt tối đa 50 khung HTTP / 10 SMS.
 */
public final class Gateway {
    private static final int HTTP_MAX = 50;
    private static final int SMS_MAX = 10;

    private final SosQueue queue;
    private final EventLog log;
    private final Context context;

    public Gateway(Context context, SosQueue queue, EventLog log) {
        this.context = context;
        this.queue = queue;
        this.log = log;
    }

    /** Trả true nếu đã đẩy được ít nhất một khung ra ngoài. */
    public boolean flush(String serverUrl, String smsNumber) {
        List<JSONObject> unsent = queue.takeUnsent(Math.max(HTTP_MAX, SMS_MAX));
        if (unsent.isEmpty()) return false;
        boolean httpOk = false;
        if (serverUrl != null && !serverUrl.trim().isEmpty() && hasNetwork()) {
            httpOk = postHttp(serverUrl.trim(), unsent);
        }
        if (httpOk) {
            for (JSONObject o : unsent) queue.markSent(o.optString("frame_id"), "http");
            log.write("gateway_sent", EventLog.fields("via", "http", "count", String.valueOf(unsent.size())));
            return true;
        }
        if (smsNumber != null && !smsNumber.trim().isEmpty() && hasSendSms()) {
            int sent = 0;
            for (JSONObject o : unsent) {
                if (sent >= SMS_MAX) break;
                if (sendSms(smsNumber.trim(), o)) sent++;
            }
            if (sent > 0) {
                log.write("gateway_sent", EventLog.fields("via", "sms", "count", String.valueOf(sent)));
                return true;
            }
        }
        return false;
    }

    private boolean postHttp(String serverUrl, List<JSONObject> unsent) {
        HttpURLConnection conn = null;
        try {
            JSONArray frames = new JSONArray();
            for (JSONObject o : unsent) frames.put(o);
            JSONObject body = new JSONObject();
            body.put("device_time_ms", System.currentTimeMillis());
            body.put("frames", frames);
            byte[] payload = body.toString().getBytes(StandardCharsets.UTF_8);
            conn = (HttpURLConnection) new URL(serverUrl).openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            conn.setConnectTimeout(5_000);
            conn.setReadTimeout(5_000);
            conn.setDoOutput(true);
            try (OutputStream os = conn.getOutputStream()) {
                os.write(payload);
            }
            int code = conn.getResponseCode();
            return code >= 200 && code < 300;
        } catch (Exception e) {
            log.write("gateway_http_error", EventLog.fields("error", String.valueOf(e)));
            return false;
        } finally {
            if (conn != null) conn.disconnect();
        }
    }

    /** Nội dung SMS ASCII không dấu, ≤160 ký tự (UCS-2 chỉ được 70 — quy tắc §10). */
    static String smsText(JSONObject o) {
        return "SOS " + o.optString("source")
                + " " + o.optDouble("latitude", 0) + "," + o.optDouble("longitude", 0)
                + " hop" + o.optInt("hop", 0)
                + " bat" + o.optInt("battery", 0)
                + " trig" + o.optInt("trigger", 0);
    }

    private boolean sendSms(String number, JSONObject o) {
        try {
            String text = smsText(o);
            if (text.length() > 160) text = text.substring(0, 160);
            SmsManager sm = Build.VERSION.SDK_INT >= 31
                    ? context.getSystemService(SmsManager.class)
                    : SmsManager.getDefault();
            if (sm == null) return false;
            sm.sendTextMessage(number, null, text, null, null);
            return true;
        } catch (Exception e) {
            log.write("gateway_sms_error", EventLog.fields("error", String.valueOf(e)));
            return false;
        }
    }

    private boolean hasNetwork() {
        ConnectivityManager cm = context.getSystemService(ConnectivityManager.class);
        if (cm == null) return false;
        NetworkInfo info = cm.getActiveNetworkInfo();
        return info != null && info.isConnected();
    }

    private boolean hasSendSms() {
        if (Build.VERSION.SDK_INT >= 23) {
            return context.checkSelfPermission(Manifest.permission.SEND_SMS)
                    == PackageManager.PERMISSION_GRANTED;
        }
        return true;
    }
}
