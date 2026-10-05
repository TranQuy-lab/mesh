package org.rescuemesh.g0;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Launcher: cấp quyền (Bluetooth + vị trí), bật node SOS, hiển thị la bàn
 * chỉ hướng tới SOS đã nhận + cấu hình cổng ra (server / SMS).
 */
public final class MainActivity extends Activity implements SensorEventListener {
    private static final int REQUEST = 71;
    private TextView status, gpsInfo, sosList;
    private Button sosButton;
    private EditText serverUrl, smsNumber;
    private SensorManager sensorManager;
    private float headingDeg = Float.NaN;
    private final Handler uiTick = new Handler(Looper.getMainLooper());

    private final Runnable refresh = new Runnable() {
        @Override public void run() {
            try {
                renderState();
            } finally {
                uiTick.postDelayed(this, 1_000L);
            }
        }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        SharedPreferences prefs = getSharedPreferences("rescuemesh", Context.MODE_PRIVATE);

        ScrollView scroll = new ScrollView(this);
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(40, 40, 40, 40);

        TextView title = new TextView(this);
        title.setText("RescueSOS-Phone\nSOS đi theo người — mạng BLE");
        title.setTextSize(20);

        status = new TextView(this);
        status.setPadding(0, 24, 0, 24);
        gpsInfo = new TextView(this);
        sosList = new TextView(this);
        sosList.setPadding(0, 24, 0, 24);

        sosButton = new Button(this);
        sosButton.setText("SOS");
        sosButton.setOnClickListener(v -> {
            sendServiceCommand("sos");
            ProbeService.UI.status = "Đã phát SOS bằng tay.";
        });

        Button cancelFall = new Button(this);
        cancelFall.setText("Huỷ đếm ngược ngã");
        cancelFall.setOnClickListener(v -> {
            ProbeService.cancelCountdown();
            status.setText("Đã huỷ đếm ngược.");
        });

        Button stop = new Button(this);
        stop.setText("Tắt node");
        stop.setOnClickListener(v -> {
            stopService(new Intent(this, ProbeService.class));
            setSosInactive();
            status.setText("Node đã tắt.");
        });

        TextView cfgTitle = new TextView(this);
        cfgTitle.setText("Cổng ra (khâu ③)");
        cfgTitle.setPadding(0, 40, 0, 8);
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
        });

        box.addView(title);
        box.addView(status);
        box.addView(gpsInfo);
        box.addView(sosButton);
        box.addView(cancelFall);
        box.addView(stop);
        box.addView(sosList);
        box.addView(cfgTitle);
        box.addView(serverUrl);
        box.addView(smsNumber);
        box.addView(saveCfg);
        scroll.addView(box);
        setContentView(scroll);

        startNode();
        uiTick.post(refresh);
    }

    private void renderState() {
        ProbeService.UiState s = ProbeService.UI;
        if (s.running) setSosActive();
        StringBuilder sb = new StringBuilder();
        if (s.running) {
            sb.append(String.format(Locale.US,
                    "GPS: %.5f, %.5f (độ chính xác cấp %d)\n", s.ownLat, s.ownLon, s.gpsFix));
            if (s.countdownEndMs > System.currentTimeMillis()) {
                long sec = (s.countdownEndMs - System.currentTimeMillis()) / 1000;
                sb.append("ĐẾM NGƯỢC NGÃ: ").append(sec).append(" s — huỷ nếu không phải ngã!\n");
            }
            sb.append("Hàng đợi chờ cổng ra: ").append(s.pendingOut).append(" khung\n");
            sb.append("Hướng máy (la bàn): ").append(headingText()).append("\n");
        }
        gpsInfo.setText(sb.toString());

        List<SosRecord> recent;
        synchronized (s.recent) {
            recent = new ArrayList<>(s.recent);
        }
        if (recent.isEmpty()) {
            sosList.setText("Chưa có SOS nào (mình phát hoặc nhận qua BLE).");
        } else {
            StringBuilder lb = new StringBuilder("SOS gần đây (mình + nhận được):\n");
            int shown = 0;
            for (SosRecord r : recent) {
                if (shown++ >= 8) break;
                lb.append(descibe(r));
            }
            sosList.setText(lb.toString());
        }
    }

    private String descibe(SosRecord r) {
        if (Double.isNaN(ProbeService.UI.ownLat) || Double.isNaN(ProbeService.UI.ownLon)
                || (r.lat == 0 && r.lon == 0)) {
            return String.format(Locale.US, "#%08x trig%d hop%d\n", r.srcId, r.trigger, r.hop);
        }
        double dist = Geo.distanceMeters(ProbeService.UI.ownLat, ProbeService.UI.ownLon, r.lat, r.lon);
        double bearing = Geo.bearingDegrees(ProbeService.UI.ownLat, ProbeService.UI.ownLon, r.lat, r.lon);
        return String.format(Locale.US, "%s #%08x • %,.0f m • %s • trig%d hop%d\n",
                Geo.octant(bearing), r.srcId, dist, triggerName(r.trigger), r.trigger, r.hop);
    }

    private String triggerName(int trigger) {
        switch (trigger) {
            case ProbeService.TRIGGER_FALL: return "ngã";
            case ProbeService.TRIGGER_H7: return "chìm";
            default: return "tay";
        }
    }

    private String headingText() {
        if (Float.isNaN(headingDeg)) return "chưa có (đang đọc la bàn)";
        return String.format(Locale.US, "%.0f° %s", headingDeg, Geo.octant(headingDeg));
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
        setSosActive();
        status.setText("Node đang chạy: BLE mesh + cảm biến + GNSS.\nCó thể khoá màn hình.");
    }

    private void setSosActive() {
        if (sosButton == null) return;
        sosButton.setText("SOS (bấm để phát khung mới)");
        sosButton.setTextColor(Color.WHITE);
        sosButton.setBackgroundTintList(ColorStateList.valueOf(Color.rgb(198, 40, 40)));
    }

    private void setSosInactive() {
        if (sosButton == null) return;
        sosButton.setText("SOS");
        sosButton.setTextColor(Color.BLACK);
        sosButton.setBackgroundTintList(null);
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

    // --- La bàn --------------------------------------------------------------

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
