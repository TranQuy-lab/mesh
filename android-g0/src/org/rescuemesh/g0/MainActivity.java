package org.rescuemesh.g0;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

/** Small no-frills launcher: grant permissions once, then start/stop the node. */
public final class MainActivity extends Activity {
    private static final int REQUEST = 71;
    private TextView status;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(40, 40, 40, 40);
        TextView title = new TextView(this);
        title.setText("RescueMesh v1.0\nĐiện thoại cứu hộ ngoại tuyến");
        title.setTextSize(22);
        status = new TextView(this);
        status.setText("Nhấn Bật nút mạng để bắt đầu.");
        status.setPadding(0, 30, 0, 30);
        Button start = new Button(this);
        start.setText("Bật nút mạng");
        start.setOnClickListener(v -> startNode());
        Button stop = new Button(this);
        stop.setText("Tắt nút mạng");
        stop.setOnClickListener(v -> {
            stopService(new Intent(this, ProbeService.class));
            status.setText("Đã tắt.");
        });
        box.addView(title); box.addView(status); box.addView(start); box.addView(stop);
        setContentView(box);
    }

    private void startNode() {
        if (Build.VERSION.SDK_INT >= 31) {
            requestPermissions(new String[]{Manifest.permission.BLUETOOTH_SCAN,
                    Manifest.permission.BLUETOOTH_ADVERTISE,
                    Manifest.permission.BLUETOOTH_CONNECT,
                    Manifest.permission.POST_NOTIFICATIONS}, REQUEST);
            status.setText("Hãy chấp nhận các quyền Bluetooth và thông báo.");
            return;
        }
        launchService();
    }

    private void launchService() {
        Intent i = new Intent(this, ProbeService.class);
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(i); else startService(i);
        status.setText("Đang phát SOS, quét và chuyển tiếp gói BLE…\nCó thể khóa màn hình.");
    }

    @Override public void onRequestPermissionsResult(int request, String[] permissions, int[] grants) {
        super.onRequestPermissionsResult(request, permissions, grants);
        if (request == REQUEST) {
            boolean ok = true;
            for (int g : grants) ok &= g == PackageManager.PERMISSION_GRANTED;
            if (ok) { launchService(); status.setText("Đã cấp quyền. Nút mạng đang chạy."); }
            else status.setText("Cần cấp quyền Bluetooth để chạy.");
        }
    }
}
