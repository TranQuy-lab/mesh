package org.rescuemesh.g0;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * App gộp một ứng dụng duy nhất: vai trò node SOS (người dân — chạy qua
 * ProbeService nền) + vai trò cứu hộ (bản đồ + la bàn + danh sách SOS đọc
 * server). Ba tab: Bản đồ / La bàn / Cấu hình.
 */
public final class MainActivity extends Activity implements SensorEventListener {
    private static final int REQUEST = 71;
    private static final int COLOR_SOS = Color.rgb(229, 57, 53);
    private static final int COLOR_SURFACE = Color.rgb(23, 28, 36);
    private static final int COLOR_BG = Color.rgb(14, 17, 22);
    private static final int COLOR_TEXT = Color.rgb(234, 240, 247);
    private static final int COLOR_DIM = Color.rgb(147, 161, 179);
    private static final int COLOR_BORDER = Color.rgb(42, 51, 64);
    private static final int COLOR_SAFE = Color.rgb(67, 160, 71);

    private TextView status, gpsInfo, sosList, compassTitle, compassDist, compassMeta, compassHint;
    private TextView arrowView;
    private Button sosButton;
    private EditText serverUrl, smsNumber;
    private WebView webView;
    private FrameLayout mapSection, compassSection, configSection;
    private Button tabMap, tabCompass, tabConfig;
    private String selectedSource;
    private SensorManager sensorManager;
    private float headingDeg = Float.NaN;
    private final Handler uiTick = new Handler(Looper.getMainLooper());

    /** Bản ghi hiển thị gộp từ hai nguồn (BLE + server). */
    private static final class SosView {
        String source;
        Double lat, lon;
        int trigger = 1;
        String triggerName = "?";
        int hop = -1, battery = -1, gpsFix;
        long ageS = -1;
        int frames = 1;
    }

    private final Runnable refresh = new Runnable() {
        @Override public void run() {
            try {
                renderState();
                renderMap();
            } finally {
                uiTick.postDelayed(this, 1_000L);
            }
        }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        SharedPreferences prefs = getSharedPreferences("rescuemesh", Context.MODE_PRIVATE);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(COLOR_BG);
        root.setPadding(24, 24, 24, 0);

        TextView title = new TextView(this);
        title.setText("RescueSOS — node + cứu hộ");
        title.setTextSize(20);
        title.setTextColor(COLOR_TEXT);
        title.setPadding(0, 0, 0, 16);

        LinearLayout tabs = new LinearLayout(this);
        tabs.setOrientation(LinearLayout.HORIZONTAL);
        tabMap = tabButton("Bản đồ");
        tabCompass = tabButton("La bàn");
        tabConfig = tabButton("Cấu hình");
        tabs.addView(tabMap); tabs.addView(tabCompass); tabs.addView(tabConfig);

        FrameLayout content = new FrameLayout(this);

        // --- Tab Bản đồ: WebView + Leaflet (asset, không cần dependency) -------
        mapSection = new FrameLayout(this);
        webView = new WebView(this);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        webView.setBackgroundColor(COLOR_BG);
        webView.loadUrl("file:///android_asset/map.html");
        mapSection.addView(webView);

        // --- Tab La bàn: kim + trạng thái + danh sách SOS ----------------------
        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(COLOR_BG);
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(16, 16, 16, 32);

        status = new TextView(this);
        status.setTextColor(COLOR_TEXT);
        status.setPadding(0, 8, 0, 8);
        gpsInfo = new TextView(this);
        gpsInfo.setTextColor(COLOR_TEXT);

        sosButton = new Button(this);
        sosButton.setText("SOS (bấm để phát khung mới)");
        sosButton.setTextColor(Color.WHITE);
        sosButton.setOnClickListener(v -> {
            sendServiceCommand("sos");
            status.setText("Đã phát SOS bằng tay.");
        });

        Button cancelFall = new Button(this);
        cancelFall.setText("Huỷ đếm ngược ngã");
        cancelFall.setOnClickListener(v -> {
            ProbeService.cancelCountdown();
            status.setText("Đã huỷ đếm ngược.");
        });

        Button stop = new Button(this);
        stop.setText("Tắt node");
        stop.setTextColor(Color.BLACK);
        stop.setOnClickListener(v -> {
            stopService(new Intent(this, ProbeService.class));
            status.setText("Node đã tắt — bản đồ vẫn xem được.");
        });

        compassTitle = new TextView(this);
        compassTitle.setTextSize(18);
        compassTitle.setTextColor(COLOR_TEXT);
        compassTitle.setGravity(Gravity.CENTER);
        compassTitle.setPadding(0, 24, 0, 8);

        FrameLayout dial = new FrameLayout(this);
        dial.setBackgroundColor(COLOR_SURFACE);
        dial.setPadding(24, 24, 24, 24);
        arrowView = new TextView(this);
        arrowView.setText("▲");
        arrowView.setTextSize(110);
        arrowView.setGravity(Gravity.CENTER);
        dial.addView(arrowView);
        LinearLayout.LayoutParams dialLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 600);
        dialLp.topMargin = 8;

        compassDist = new TextView(this);
        compassDist.setTextSize(34);
        compassDist.setTextColor(COLOR_TEXT);
        compassDist.setGravity(Gravity.CENTER);
        compassMeta = new TextView(this);
        compassMeta.setTextColor(COLOR_DIM);
        compassMeta.setGravity(Gravity.CENTER);
        compassHint = new TextView(this);
        compassHint.setTextColor(COLOR_DIM);
        compassHint.setGravity(Gravity.CENTER);
        compassHint.setPadding(0, 8, 0, 8);

        sosList = new TextView(this);
        sosList.setTextColor(COLOR_TEXT);
        sosList.setPadding(0, 24, 0, 0);
        sosList.setOnClickListener(v -> selectNext());

        box.addView(status);
        box.addView(gpsInfo);
        box.addView(sosButton);
        box.addView(cancelFall);
        box.addView(stop);
        box.addView(compassTitle);
        box.addView(dial, dialLp);
        box.addView(compassDist);
        box.addView(compassMeta);
        box.addView(compassHint);
        box.addView(sosList);
        compassSection = new FrameLayout(this);
        compassSection.addView(scroll);
        scroll.addView(box);

        // --- Tab Cấu hình ------------------------------------------------------
        LinearLayout cfg = new LinearLayout(this);
        cfg.setOrientation(LinearLayout.VERTICAL);
        cfg.setPadding(16, 16, 16, 32);
        TextView cfgTitle = new TextView(this);
        cfgTitle.setText("Cổng ra + nguồn bản đồ (khâu ③④)");
        cfgTitle.setTextColor(COLOR_TEXT);
        serverUrl = new EditText(this);
        serverUrl.setHint("URL server, vd http://192.168.1.10:8787/api/sos");
        serverUrl.setText(prefs.getString("server_url", ""));
        smsNumber = new EditText(this);
        smsNumber.setHint("Số SMS dự phòng (tuỳ chọn)");
        smsNumber.setText(prefs.getString("sms_number", ""));
        Button saveCfg = new Button(this);
        saveCfg.setText("Lưu cấu hình");
        saveCfg.setOnClickListener(v -> {
            prefs.edit()
                    .putString("server_url", serverUrl.getText().toString().trim())
                    .putString("sms_number", smsNumber.getText().toString().trim())
                    .apply();
            status.setText("Đã lưu cấu hình cổng ra.");
            switchTab(0);
        });
        TextView about = new TextView(this);
        about.setTextColor(COLOR_DIM);
        about.setText("Cùng một app làm cả hai vai trò: node SOS chạy nền (BLE + cảm biến "
                + "+ cổng ra), phần này xem bản đồ/la bàn từ server. Kẹt Internet thì "
                + "ghim SOS + la bàn vẫn chạy, chỉ trống nền bản đồ.");
        about.setPadding(0, 24, 0, 0);
        cfg.addView(cfgTitle);
        cfg.addView(serverUrl);
        cfg.addView(smsNumber);
        cfg.addView(saveCfg);
        cfg.addView(about);
        configSection = new FrameLayout(this);
        configSection.addView(cfg);

        content.addView(mapSection);
        content.addView(compassSection);
        content.addView(configSection);

        root.addView(title);
        root.addView(tabs);
        root.addView(content, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));
        setContentView(root);

        switchTab(0);
        startNode();
        uiTick.post(refresh);
    }

    private Button tabButton(String label) {
        Button b = new Button(this);
        b.setText(label);
        b.setTextColor(Color.WHITE);
        return b;
    }

    private void switchTab(int which) {
        mapSection.setVisibility(which == 0 ? View.VISIBLE : View.GONE);
        compassSection.setVisibility(which == 1 ? View.VISIBLE : View.GONE);
        configSection.setVisibility(which == 2 ? View.VISIBLE : View.GONE);
        tabMap.setBackgroundTintList(android.content.res.ColorStateList.valueOf(
                which == 0 ? COLOR_SOS : COLOR_SURFACE));
        tabCompass.setBackgroundTintList(android.content.res.ColorStateList.valueOf(
                which == 1 ? COLOR_SOS : COLOR_SURFACE));
        tabConfig.setBackgroundTintList(android.content.res.ColorStateList.valueOf(
                which == 2 ? COLOR_SOS : COLOR_SURFACE));
    }

    // --- Dữ liệu gộp (server + BLE) -------------------------------------------

    private List<SosView> buildViewList() {
        List<SosView> out = new ArrayList<>();
        List<String> sources = new ArrayList<>();
        synchronized (ProbeService.UI.remote) {
            for (JSONObject o : ProbeService.UI.remote) {
                SosView v = new SosView();
                v.source = o.optString("source");
                v.lat = o.has("latitude") && !o.isNull("latitude") ? o.optDouble("latitude") : null;
                v.lon = o.has("longitude") && !o.isNull("longitude") ? o.optDouble("longitude") : null;
                v.trigger = o.optInt("trigger", 1);
                v.triggerName = o.optString("trigger_name", "?");
                v.hop = o.optInt("hop", -1);
                v.battery = o.optInt("battery", -1);
                v.gpsFix = o.optInt("gps_fix", 0);
                v.ageS = o.optLong("age_s", -1);
                v.frames = o.optInt("frames", 1);
                if (v.source != null && !v.source.isEmpty()) {
                    out.add(v);
                    sources.add(v.source);
                }
            }
        }
        synchronized (ProbeService.UI.recent) {
            for (SosRecord r : ProbeService.UI.recent) {
                String src = String.format(Locale.US, "0x%08x", r.srcId);
                if (sources.contains(src)) continue;
                SosView v = new SosView();
                v.source = src;
                if (!(r.lat == 0 && r.lon == 0)) { v.lat = r.lat; v.lon = r.lon; }
                v.trigger = r.trigger;
                v.triggerName = triggerName(r.trigger);
                v.hop = r.hop;
                v.battery = r.battery;
                v.gpsFix = r.gpsFix;
                out.add(v);
            }
        }
        return out;
    }

    private static String triggerName(int trigger) {
        switch (trigger) {
            case ProbeService.TRIGGER_FALL: return "Ngã (IMU)";
            case ProbeService.TRIGGER_H7: return "Chìm (H7)";
            default: return "Bấm tay";
        }
    }

    private void selectNext() {
        List<SosView> list = buildViewList();
        if (list.isEmpty()) { selectedSource = null; return; }
        int idx = -1;
        for (int i = 0; i < list.size(); i++) {
            if (list.get(i).source.equals(selectedSource)) { idx = i; break; }
        }
        selectedSource = list.get((idx + 1) % list.size()).source;
    }

    // --- Vẽ UI ----------------------------------------------------------------

    private void renderState() {
        ProbeService.UiState s = ProbeService.UI;
        if (s.running) {
            sosButton.setText("SOS (bấm để phát khung mới)");
            sosButton.setTextColor(Color.WHITE);
        }
        StringBuilder sb = new StringBuilder();
        if (s.running) {
            sb.append(String.format(Locale.US,
                    "GPS: %.5f, %.5f (cấp %d) • hàng đợi cổng ra: %d khung\n",
                    s.ownLat, s.ownLon, s.gpsFix, s.pendingOut));
            if (s.countdownEndMs > System.currentTimeMillis()) {
                long sec = (s.countdownEndMs - System.currentTimeMillis()) / 1000;
                sb.append("ĐẾM NGƯỢC NGÃ: ").append(sec).append(" s — huỷ nếu không phải ngã!\n");
            }
        } else {
            sb.append("Node đang tắt — bấm SOS để bật lại.\n");
        }
        gpsInfo.setText(sb.toString());

        List<SosView> list = buildViewList();
        SosView target = null;
        for (SosView v : list) if (v.source.equals(selectedSource)) target = v;
        if (target == null && !list.isEmpty()) target = list.get(0);
        if (target != null && selectedSource == null) selectedSource = target.source;

        compassTitle.setText(target == null ? "Chưa có SOS nào" : "SOS " + target.source);
        boolean hasPos = target != null && target.lat != null && target.lon != null
                && !Double.isNaN(s.ownLat);
        if (hasPos) {
            double dist = Geo.distanceMeters(s.ownLat, s.ownLon, target.lat, target.lon);
            double bearing = Geo.bearingDegrees(s.ownLat, s.ownLon, target.lat, target.lon);
            compassDist.setText(dist >= 1000
                    ? String.format(Locale.US, "%.1f km", dist / 1000)
                    : String.format(Locale.US, "%d m", Math.round(dist)));
            compassMeta.setText(String.format(Locale.US, "hướng %s (%.0f°)%s",
                    Geo.octant(bearing), bearing,
                    Float.isNaN(headingDeg) ? "" : String.format(Locale.US, " • máy đang %.0f°", headingDeg)));
            float rotate = Float.isNaN(headingDeg) ? (float) bearing : (float) (bearing - headingDeg);
            arrowView.setRotation(rotate);
            arrowView.setTextColor(0xFFE53935 | 0xFF000000);
        } else {
            compassDist.setText("—");
            compassMeta.setText("");
            compassHint.setText(target == null
                    ? "Node phát SOS hoặc server có SOS sẽ hiện ở đây (cấu hình URL ở tab Cấu hình)."
                    : "SOS chưa có toạ độ (mất GPS) hoặc máy chưa có vị trí.");
        }

        StringBuilder lb = new StringBuilder();
        if (target != null) {
            lb.append(String.format(Locale.US, "%s • hop %d • pin %s • GPS cấp %d%s\n",
                    target.triggerName, target.hop,
                    target.battery >= 0 ? target.battery + "/15" : "?",
                    target.gpsFix,
                    target.ageS >= 0 ? " • " + target.ageS + "s trước" : ""));
        }
        if (list.size() > 1) {
            lb.append("\nChạm để đổi SOS đang theo (").append(list.size()).append(" SOS).");
        }
        for (int i = 0; i < list.size() && i < 6; i++) {
            SosView v = list.get(i);
            lb.append(String.format(Locale.US, "\n%s %s%s", v.source, v.triggerName,
                    v.source.equals(selectedSource) ? " • đang theo" : ""));
        }
        sosList.setText(lb.toString());
    }

    private void renderMap() {
        if (webView == null) return;
        try {
            List<SosView> list = buildViewList();
            JSONArray arr = new JSONArray();
            for (SosView v : list) {
                JSONObject o = new JSONObject();
                o.put("source", v.source);
                if (v.lat != null && v.lon != null) {
                    o.put("latitude", v.lat);
                    o.put("longitude", v.lon);
                }
                o.put("trigger", v.trigger);
                o.put("trigger_name", v.triggerName);
                o.put("hop", v.hop);
                o.put("battery", v.battery);
                arr.put(o);
            }
            ProbeService.UiState s = ProbeService.UI;
            String own = Double.isNaN(s.ownLat) ? "null,null" :
                    String.format(Locale.US, "%.6f,%.6f", s.ownLat, s.ownLon);
            webView.evaluateJavascript(
                    "window.setOwn(" + own + ");window.setSos(" + arr + ");", null);
        } catch (Exception ignored) {}
    }

    private void sendServiceCommand(String cmd) {
        Intent i = new Intent(this, ProbeService.class);
        i.putExtra("cmd", cmd);
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(i); else startService(i);
    }

    private void startNode() {
        List<String> needed = new ArrayList<>();
        if (Build.VERSION.SDK_INT >= 31) {
            needed.add(Manifest.permission.BLUETOOTH_SCAN);
            needed.add(Manifest.permission.BLUETOOTH_ADVERTISE);
            needed.add(Manifest.permission.BLUETOOTH_CONNECT);
        }
        needed.add(Manifest.permission.ACCESS_FINE_LOCATION);
        if (Build.VERSION.SDK_INT >= 33) {
            needed.add(Manifest.permission.POST_NOTIFICATIONS);
        }
        boolean allGranted = true;
        for (String p : needed) {
            allGranted &= checkSelfPermission(p) == PackageManager.PERMISSION_GRANTED;
        }
        if (!allGranted) {
            requestPermissions(needed.toArray(new String[0]), REQUEST);
            status.setText("Hãy chấp nhận quyền Bluetooth, vị trí và thông báo.");
            return;
        }
        launchService();
    }

    private void launchService() {
        Intent i = new Intent(this, ProbeService.class);
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(i); else startService(i);
        status.setText("Node đang chạy: BLE mesh + cảm biến + GNSS.\nCó thể khoá màn hình.");
    }

    @Override public void onRequestPermissionsResult(int request, String[] permissions, int[] grants) {
        super.onRequestPermissionsResult(request, permissions, grants);
        if (request == REQUEST) {
            boolean ok = true;
            for (int g : grants) ok &= g == PackageManager.PERMISSION_GRANTED;
            if (ok) { launchService(); status.setText("Đã cấp quyền. Node đang chạy."); }
            else status.setText("Cần quyền Bluetooth + vị trí để chạy.");
        }
    }

    // --- La bàn (từ-trường) ---------------------------------------------------

    private final float[] rotMatrix = new float[9];
    private final float[] rotVals = new float[3];
    private final float[] gravityVals = new float[3];
    private final float[] magVals = new float[3];
    private boolean hasGravity, hasMag;

    @Override public void onResume() {
        super.onResume();
        uiTick.post(refresh);
        sensorManager = getSystemService(SensorManager.class);
        if (sensorManager != null) {
            Sensor accel = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
            Sensor mag = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
            if (accel != null) sensorManager.registerListener(this, accel, SensorManager.SENSOR_DELAY_UI);
            if (mag != null) sensorManager.registerListener(this, mag, SensorManager.SENSOR_DELAY_UI);
        }
    }

    @Override public void onPause() {
        super.onPause();
        uiTick.removeCallbacks(refresh);
        if (sensorManager != null) sensorManager.unregisterListener(this);
    }

    @Override public void onSensorChanged(SensorEvent event) {
        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
            System.arraycopy(event.values, 0, gravityVals, 0, 3);
            hasGravity = true;
        } else if (event.sensor.getType() == Sensor.TYPE_MAGNETIC_FIELD) {
            System.arraycopy(event.values, 0, magVals, 0, 3);
            hasMag = true;
        }
        if (hasGravity && hasMag
                && SensorManager.getRotationMatrix(rotMatrix, null, gravityVals, magVals)) {
            SensorManager.getOrientation(rotMatrix, rotVals);
            headingDeg = (float) ((Math.toDegrees(rotVals[0]) + 360.0) % 360.0);
        }
    }

    @Override public void onAccuracyChanged(Sensor sensor, int accuracy) {}
}
