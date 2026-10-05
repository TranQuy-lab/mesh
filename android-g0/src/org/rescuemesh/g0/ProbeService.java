package org.rescuemesh.g0;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.AdvertiseData;
import android.bluetooth.le.AdvertiseCallback;
import android.bluetooth.le.AdvertiseSettings;
import android.bluetooth.le.AdvertisingSet;
import android.bluetooth.le.AdvertisingSetCallback;
import android.bluetooth.le.AdvertisingSetParameters;
import android.bluetooth.le.BluetoothLeAdvertiser;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.hardware.GeomagneticField;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;
import android.os.SystemClock;
import android.provider.Settings;
import android.util.Log;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.nio.charset.StandardCharsets;

/**
 * Node SOS đầy đủ (khâu ①+②+③): IMU phát hiện ngã (T1) + H7 barometer → SOS
 * tự động có đếm ngược huỷ; BLE quét + quảng bá nhiều khung (lưu–mang–tiếp,
 * hàng đợi bền qua restart); GNSS thật ghi toạ độ vào khung; cổng ra đẩy hàng
 * đợi lên server (HTTP) hoặc SMS dự phòng theo chu kỳ.
 */
public final class ProbeService extends Service implements SensorEventListener {
    private static final String TAG = "RescueMeshG0";
    private static final String CHANNEL = "rescuemesh_g0";
    private static final int NOTIFICATION_ID = 7100;
    private static final int COMPANY_ID_LAB = 0xFFFF;
    private static final byte[] DEVICE_KEY =
            "device-key-for-tests".getBytes(StandardCharsets.UTF_8);
    private static final String SOS_GOLDEN_HEX =
            "46f72a89abcdef399de83fcb3d2d53bc4c1ba811078a6028";
    private static final byte[] SOS_GOLDEN = SosCodec.packSos(
            0x89abcdefL, 12345, 21.028511, 105.804817,
            1, 2, 3, 11, 3, 0, 7, 15, 42, DEVICE_KEY);

    static final int TRIGGER_BUTTON = 1;
    static final int TRIGGER_FALL = 2;
    static final int TRIGGER_H7 = 3;
    static final long COUNTDOWN_MS = 30_000L;
    private static final int RELAY_OUTBOX_MAX = 8;
    private static final long ROTATE_MS = 700L;
    private static final long GATEWAY_PERIOD_MS = 60_000L;

    // --- Trạng thái cho UI (MainActivity đọc trực tiếp, poll 1 Hz) -----------
    public static final class UiState {
        public volatile boolean running;
        public volatile String status = "";
        public volatile double ownLat = Double.NaN, ownLon = Double.NaN;
        public volatile int gpsFix;
        public volatile long countdownEndMs;
        public volatile int pendingOut;
        public final List<SosRecord> recent = new ArrayList<>();
    }

    public static final UiState UI = new UiState();

    /** MainActivity gọi để huỷ đếm ngược ngã. */
    public static void cancelCountdown() {
        countdownEndMs = 0;
        UI.countdownEndMs = 0;
    }

    private static volatile long countdownEndMs;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private HandlerThread workerThread;
    private Handler worker;

    private BluetoothLeAdvertiser advertiser;
    private AdvertisingSet advertisingSet;
    private BluetoothLeScanner scanner;
    private SensorManager sensorManager;
    private Sensor accelerometer, barometer, gyroscope;
    private LocationManager locationManager;
    private SosQueue queue;
    private EventLog eventLog;
    private Gateway gateway;
    private FallDetector fallDetector = new FallDetector();
    private H7Detector h7 = new H7Detector();
    private final H7Aggregator h7agg = new H7Aggregator();

    private long localSourceId = 0x89abcdefL;
    private int ownSeq = 0;
    private byte[] ownFrame;
    private final ArrayDeque<byte[]> relayOutbox = new ArrayDeque<>();
    private boolean ownSlot = true;
    private long startedElapsedMs;
    private long scanCallbacks, goldenMatches, validProtocolFrames, messagesIssued;
    private long sensorEvents, firstSensorNs, lastSensorNs;
    private boolean advertisingStarted, scanningStarted, legacyAdvertising, bluetoothProbeStarting;
    private float ownAccuracy = Float.NaN;

    private BluetoothLeAdvertiser advertiserRef() { return advertiser; }

    // --- BLE -----------------------------------------------------------------

    private final AdvertisingSetCallback advertiseCallback = new AdvertisingSetCallback() {
        @Override public void onAdvertisingSetStarted(AdvertisingSet set, int txPower, int status) {
            if (status != ADVERTISE_SUCCESS) {
                advertisingStarted = false;
                log("advertise_start", "ok=false,error=" + status);
                return;
            }
            advertisingSet = set;
            advertisingStarted = true;
            messagesIssued = 1;
            log("advertise_start", "ok=true,legacy=true,tx_dbm=" + txPower
                    + ",connectable=false,payload_bytes=" + (ownFrame == null ? SOS_GOLDEN.length : ownFrame.length)
                    + ",messages_issued=" + messagesIssued);
            handler.postDelayed(rotator, ROTATE_MS);
        }

        @Override public void onAdvertisingDataSet(AdvertisingSet set, int status) {
            if (status != ADVERTISE_SUCCESS) {
                log("advertise_data", "ok=false,error=" + status);
            }
        }
    };

    private final AdvertiseCallback legacyAdvertiseCallback = new AdvertiseCallback() {
        @Override public void onStartSuccess(AdvertiseSettings settingsInEffect) {
            advertisingStarted = true;
            messagesIssued = 1;
            log("advertise_start", "ok=true,api=legacy,connectable=false");
            handler.postDelayed(rotator, ROTATE_MS * 4);
        }

        @Override public void onStartFailure(int errorCode) {
            advertisingStarted = false;
            log("advertise_start", "ok=false,api=legacy,error=" + errorCode);
        }
    };

    /** Quay vòng lượt quảng bá: khung của mình ↔ khung nhận được (đa hop). */
    private final Runnable rotator = new Runnable() {
        @Override public void run() {
            try {
                byte[] frame;
                byte[] own = ownFrame != null ? ownFrame : SOS_GOLDEN;
                if (ownSlot || relayOutbox.isEmpty()) {
                    frame = own;
                } else {
                    frame = relayOutbox.poll();
                    if (frame != null) relayOutbox.offer(frame);  // giữ để phát lại vòng sau
                }
                ownSlot = !ownSlot;
                if (frame != null) setAdvertisingFrame(frame);
            } finally {
                handler.postDelayed(this, legacyAdvertising ? ROTATE_MS * 4 : ROTATE_MS);
            }
        }
    };

    private final ScanCallback scanCallback = new ScanCallback() {
        @Override public void onScanResult(int callbackType, ScanResult result) {
            scanCallbacks++;
            byte[] manufacturerData = result.getScanRecord() == null ? null
                    : result.getScanRecord().getManufacturerSpecificData(COMPANY_ID_LAB);
            if (manufacturerData != null && manufacturerData.length == SosCodec.SIZE
                    && SosCodec.verify(manufacturerData, DEVICE_KEY)) {
                validProtocolFrames++;
                if (Arrays.equals(SOS_GOLDEN, manufacturerData)) {
                    goldenMatches++;
                    return;
                }
                onValidFrame(manufacturerData);
            }
        }

        @Override public void onBatchScanResults(List<ScanResult> results) {
            for (ScanResult result : results) onScanResult(0, result);
        }

        @Override public void onScanFailed(int errorCode) {
            scanningStarted = false;
            log("scan_start", "ok=false,error=" + errorCode);
        }
    };

    private void onValidFrame(byte[] frame) {
        SosRecord rec = SosRecord.unpack(frame);
        boolean isNew = queue.addReceived(frame, System.currentTimeMillis());
        if (!isNew) return;
        long now = System.currentTimeMillis();
        synchronized (UI.recent) {
            UI.recent.add(0, rec);
            while (UI.recent.size() > 20) UI.recent.remove(UI.recent.size() - 1);
        }
        eventLog.write("frame_rx", frameFields(rec, "rssi", "n/a"));
        int route = frame[1] & 0xff;
        int ttl = (route >>> 4) & 0x0f;
        if (ttl > 0) {
            byte[] forwarded = frame.clone();
            int hop = route & 0x0f;
            forwarded[1] = (byte) (((ttl - 1) << 4) | Math.min(15, hop == 15 ? 0 : hop + 1));
            offerRelay(forwarded);
        }
        updateUiStatus();
    }

    private void offerRelay(byte[] frame) {
        while (relayOutbox.size() >= RELAY_OUTBOX_MAX) relayOutbox.poll();
        relayOutbox.offer(frame);
    }

    // --- Cảm biến ------------------------------------------------------------

    @Override public void onSensorChanged(SensorEvent event) {
        sensorEvents++;
        if (firstSensorNs == 0) firstSensorNs = event.timestamp;
        lastSensorNs = event.timestamp;
        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
            float ax = event.values[0] / SensorManager.GRAVITY_EARTH;
            float ay = event.values[1] / SensorManager.GRAVITY_EARTH;
            float az = event.values[2] / SensorManager.GRAVITY_EARTH;
            h7agg.addAccel(ax, ay, az);
            if (fallDetector.push(ax, ay, az) == FallDetector.Event.FALL_SUSPECTED) {
                onFallSuspected();
            }
        } else if (event.sensor.getType() == Sensor.TYPE_GYROSCOPE) {
            float gx = event.values[0], gy = event.values[1], gz = event.values[2];
            h7agg.addGyro(gx, gy, gz);
        } else if (event.sensor.getType() == Sensor.TYPE_PRESSURE) {
            h7agg.addPressure(event.values[0]);
        }
    }

    @Override public void onAccuracyChanged(Sensor sensor, int accuracy) {}

    private void onFallSuspected() {
        if (countdownEndMs > 0) return;
        countdownEndMs = System.currentTimeMillis() + COUNTDOWN_MS;
        UI.countdownEndMs = countdownEndMs;
        eventLog.write("fall_suspected", EventLog.fields(
                "countdown_ms", String.valueOf(COUNTDOWN_MS)));
        notifyText("Phát hiện có thể ngã", "Nhấn mở app để huỷ trong 30 giây.");
        handler.postDelayed(() -> {
            if (countdownEndMs > 0 && System.currentTimeMillis() >= countdownEndMs) {
                countdownEndMs = 0;
                UI.countdownEndMs = 0;
                issueSos(TRIGGER_FALL);
            }
        }, COUNTDOWN_MS + 200);
        updateUiStatus();
    }

    private final Runnable h7Ticker = new Runnable() {
        @Override public void run() {
            try {
                H7Aggregator.Sample s = h7agg.take();
                if (s != null && barometer != null) {
                    H7Detector.State st = h7.push(1.0f, s.pressureHpa, s.accelG, s.gyroStd);
                    if (st == H7Detector.State.SUSPECT) {
                        eventLog.write("h7_suspect", EventLog.fields(
                                "dpa", String.format(Locale.US, "%.1f", h7.dpaVisible())));
                    } else if (st == H7Detector.State.ALARM) {
                        eventLog.write("h7_alarm", EventLog.fields(
                                "dpa", String.format(Locale.US, "%.1f", h7.dpaVisible())));
                        notifyText("CẢNH BÁO: có thể đang chìm", "Đã phát SOS tự động.");
                        issueSos(TRIGGER_H7);
                    }
                }
            } finally {
                handler.postDelayed(this, 1_000L);
            }
        }
    };

    // --- GNSS ----------------------------------------------------------------

    private final LocationListener locationListener = new LocationListener() {
        @Override public void onLocationChanged(Location location) {
            UI.ownLat = location.getLatitude();
            UI.ownLon = location.getLongitude();
            ownAccuracy = location.getAccuracy();
            UI.gpsFix = ownAccuracy < 20 ? 3 : ownAccuracy < 50 ? 2 : ownAccuracy < 150 ? 1 : 0;
            eventLog.write("gps_fix", EventLog.fields(
                    "lat", String.format(Locale.US, "%.6f", UI.ownLat),
                    "lon", String.format(Locale.US, "%.6f", UI.ownLon),
                    "acc_m", String.format(Locale.US, "%.0f", ownAccuracy)));
        }
        @Override public void onStatusChanged(String p, int s, Bundle b) {}
        @Override public void onProviderEnabled(String p) {}
        @Override public void onProviderDisabled(String p) {}
    };

    private void startGnss() {
        try {
            locationManager = getSystemService(LocationManager.class);
            if (locationManager == null
                    || checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
                            != PackageManager.PERMISSION_GRANTED) {
                log("gps", "ok=false,reason=permission");
                return;
            }
            if (locationManager.getAllProviders().contains(LocationManager.GPS_PROVIDER)) {
                locationManager.requestLocationUpdates(
                        LocationManager.GPS_PROVIDER, 3_000L, 3f, locationListener, Looper.getMainLooper());
            }
            if (locationManager.getAllProviders().contains(LocationManager.NETWORK_PROVIDER)) {
                locationManager.requestLocationUpdates(
                        LocationManager.NETWORK_PROVIDER, 5_000L, 10f, locationListener, Looper.getMainLooper());
            }
            Location last = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            if (last == null) last = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
            if (last != null) {
                UI.ownLat = last.getLatitude();
                UI.ownLon = last.getLongitude();
            }
            log("gps", "ok=true");
        } catch (Exception e) {
            log("gps", "ok=false,error=" + e.getClass().getSimpleName());
        }
    }

    // --- Vòng đời ------------------------------------------------------------

    @Override public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        queue = new SosQueue(this);
        eventLog = new EventLog(this);
        gateway = new Gateway(this, queue, eventLog);
        workerThread = new HandlerThread("rescuemesh-worker");
        workerThread.start();
        worker = new Handler(workerThread.getLooper());
        startForeground(NOTIFICATION_ID, buildNotification("Đang chạy: BLE mesh + cảm biến"));
        startedElapsedMs = SystemClock.elapsedRealtime();
        localSourceId = localSourceId();
        UI.running = true;
        log("codec_selftest", "golden=" + SOS_GOLDEN_HEX.equals(SosCodec.toHex(SOS_GOLDEN))
                + ",verify=" + SosCodec.verify(SOS_GOLDEN, DEVICE_KEY));
        logCapabilities();
        startSensorProbe();
        startGnss();
        handler.post(ticker);
        handler.post(h7Ticker);
        worker.postDelayed(gatewayLoop, GATEWAY_PERIOD_MS);
        updateUiStatus();
    }

    private final Runnable gatewayLoop = new Runnable() {
        @Override public void run() {
            try {
                SharedPreferences prefs = getSharedPreferences("rescuemesh", Context.MODE_PRIVATE);
                boolean sent = gateway.flush(
                        prefs.getString("server_url", ""),
                        prefs.getString("sms_number", ""));
                if (sent) updateUiStatus();
            } catch (Exception e) {
                log("gateway", "error=" + e.getClass().getSimpleName());
            } finally {
                worker.postDelayed(this, GATEWAY_PERIOD_MS);
            }
        }
    };

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        startBluetoothProbe();
        if (intent != null && "sos".equals(intent.getStringExtra("cmd"))) {
            issueSos(TRIGGER_BUTTON);
        }
        return START_STICKY;
    }

    @Override public void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        if (worker != null) worker.removeCallbacksAndMessages(null);
        if (workerThread != null) workerThread.quitSafely();
        stopBluetoothProbe();
        if (locationManager != null) {
            try { locationManager.removeUpdates(locationListener); } catch (Exception ignored) {}
        }
        if (sensorManager != null) sensorManager.unregisterListener(this);
        UI.running = false;
        UI.countdownEndMs = 0;
        countdownEndMs = 0;
        log("stop", "elapsed_ms=" + (SystemClock.elapsedRealtime() - startedElapsedMs));
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) { return null; }

    // --- SOS -----------------------------------------------------------------

    /** Phát SOS mới (nút bấm, ngã, hoặc H7) — ghi bền + lên sóng ngay. */
    public void issueSos(int trigger) {
        ownSeq = (ownSeq + 1) & 0xff;
        long minutes = (System.currentTimeMillis() / 60_000L) & 0xff;
        double lat = Double.isNaN(UI.ownLat) ? 0.0 : UI.ownLat;
        double lon = Double.isNaN(UI.ownLon) ? 0.0 : UI.ownLon;
        byte[] frame = SosCodec.packSos(localSourceId, minutes, lat, lon,
                trigger, 1, 3, batteryLevel(), UI.gpsFix, 0, 7, 15, ownSeq, DEVICE_KEY);
        ownFrame = frame;
        queue.addOwn(frame, System.currentTimeMillis());
        SosRecord rec = SosRecord.unpack(frame);
        synchronized (UI.recent) {
            UI.recent.add(0, rec);
            while (UI.recent.size() > 20) UI.recent.remove(UI.recent.size() - 1);
        }
        eventLog.write("sos_issued", frameFields(rec, "trigger", String.valueOf(trigger)));
        log("sos_issued", "trigger=" + trigger + ",seq=" + ownSeq);
        updateUiStatus();
    }

    private int batteryLevel() {
        android.os.BatteryManager bm = getSystemService(android.os.BatteryManager.class);
        int pct = bm == null ? -1 : bm.getIntProperty(android.os.BatteryManager.BATTERY_PROPERTY_CAPACITY);
        if (pct <= 0) return 11;  // mã "không rõ" 4 bit
        return Math.min(15, pct * 15 / 100);
    }

    private void updateUiStatus() {
        UI.pendingOut = queue.unsentCount();
    }

    // --- BLE khởi động (giữ kinh nghiệm G0) -----------------------------------

    private void startBluetoothProbe() {
        if (bluetoothProbeStarting || advertiser != null || scanner != null) {
            log("bluetooth", "already_running=true");
            return;
        }
        bluetoothProbeStarting = true;
        if (!hasBluetoothPermissions()) {
            log("permission", "bluetooth=false");
            bluetoothProbeStarting = false;
            return;
        }
        BluetoothManager manager = getSystemService(BluetoothManager.class);
        BluetoothAdapter adapter = manager == null ? null : manager.getAdapter();
        if (adapter == null || !adapter.isEnabled()) {
            log("bluetooth", "ready=false,reason=adapter_disabled");
            bluetoothProbeStarting = false;
            return;
        }
        advertiser = adapter.getBluetoothLeAdvertiser();
        scanner = adapter.getBluetoothLeScanner();

        if (advertiser == null) {
            log("advertise_start", "ok=false,error=advertiser_null");
        } else {
            AdvertisingSetParameters settings = new AdvertisingSetParameters.Builder()
                    .setLegacyMode(true)
                    .setInterval(AdvertisingSetParameters.INTERVAL_LOW)
                    .setTxPowerLevel(AdvertisingSetParameters.TX_POWER_HIGH)
                    .setConnectable(false)
                    .setScannable(true)
                    .build();
            try {
                legacyAdvertising = false;
                advertiser.startAdvertisingSet(settings, advertiseData(currentFrame()), null, null, null, advertiseCallback);
            } catch (IllegalArgumentException error) {
                legacyAdvertising = false;
                log("advertise_start", "ok=false,error=callback_busy");
            }
        }

        if (scanner == null) {
            log("scan_start", "ok=false,error=scanner_null");
        } else {
            ScanSettings settings = new ScanSettings.Builder()
                    .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                    .setReportDelay(0)
                    .build();
            List<ScanFilter> filters = Arrays.asList(new ScanFilter.Builder()
                    .setManufacturerData(COMPANY_ID_LAB,
                            new byte[] {0x40}, new byte[] {(byte) 0xc0})
                    .build());
            // Một số controller Xiaomi từ chối advertise+scan đồng thời nếu scan
            // mở trước khi callback của advertiser trả về.
            handler.postDelayed(() -> {
                try {
                    scanner.startScan(filters, settings, scanCallback);
                    scanningStarted = true;
                    log("scan_start", "ok=true,mode=low_latency,filtered=true");
                } catch (IllegalArgumentException error) {
                    log("scan_start", "ok=false,error=callback_busy");
                }
            }, 1_200L);
        }
        bluetoothProbeStarting = false;
    }

    private byte[] currentFrame() {
        if (ownFrame == null) issueSos(TRIGGER_BUTTON);
        return ownFrame;
    }

    private void setAdvertisingFrame(byte[] frame) {
        if (legacyAdvertising) {
            advertiser.stopAdvertising(legacyAdvertiseCallback);
            AdvertiseSettings settings = new AdvertiseSettings.Builder()
                    .setAdvertiseMode(AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY)
                    .setTxPowerLevel(AdvertiseSettings.ADVERTISE_TX_POWER_HIGH)
                    .setConnectable(false).setTimeout(0).build();
            advertiser.startAdvertising(settings, advertiseData(frame), legacyAdvertiseCallback);
        } else if (advertisingSet != null) {
            advertisingSet.setAdvertisingData(advertiseData(frame));
        }
    }

    private long localSourceId() {
        String id = Settings.Secure.getString(getContentResolver(), Settings.Secure.ANDROID_ID);
        if (id == null) return 0x89abcdefL;
        return ((long) id.hashCode()) & 0xffff_ffffL;
    }

    private static AdvertiseData advertiseData(byte[] frame) {
        return new AdvertiseData.Builder()
                .setIncludeDeviceName(false)
                .setIncludeTxPowerLevel(false)
                .addManufacturerData(COMPANY_ID_LAB, frame)
                .build();
    }

    // --- Cảm biến khởi động + tổng hợp H7 -------------------------------------

    private void startSensorProbe() {
        sensorManager = getSystemService(SensorManager.class);
        if (sensorManager == null) return;
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        barometer = sensorManager.getDefaultSensor(Sensor.TYPE_PRESSURE);
        gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        if (accelerometer != null) {
            boolean ok = sensorManager.registerListener(this, accelerometer, 50_000, 2_000_000);
            log("sensor_start", "accelerometer_ok=" + ok + ",period_us=50000");
        }
        if (gyroscope != null) {
            sensorManager.registerListener(this, gyroscope, 50_000, 2_000_000);
        }
        if (barometer != null) {
            sensorManager.registerListener(this, barometer, 1_000_000);
            log("sensor_start", "barometer=" + barometer.getName());
        } else {
            log("sensor_start", "barometer=absent,h7_disabled");
        }
    }

    /** Tổng hợp 1 s: trung bình |a| (g), std gyro (°/s), áp suất mới nhất (hPa). */
    static final class H7Aggregator {
        static final class Sample {
            final float accelG, gyroStd, pressureHpa;
            Sample(float a, float g, float p) { accelG = a; gyroStd = g; pressureHpa = p; }
        }

        private float accSum, accN;
        private float gyroSum, gyroSumSq, gyroN;
        private float pressure = Float.NaN;

        synchronized void addAccel(float ax, float ay, float az) {
            accSum += (float) Math.sqrt(ax * ax + ay * ay + az * az);
            accN++;
        }

        synchronized void addGyro(float gx, float gy, float gz) {
            float mag = (float) Math.sqrt(gx * gx + gy * gy + gz * gz);
            gyroSum += mag; gyroSumSq += mag * mag; gyroN++;
        }

        synchronized void addPressure(float hpa) { pressure = hpa; }

        synchronized Sample take() {
            if (accN == 0 || gyroN == 0 || Float.isNaN(pressure)) return null;
            float accelG = accSum / accN;
            float mean = gyroSum / gyroN;
            float std = (float) Math.sqrt(Math.max(0f, gyroSumSq / gyroN - mean * mean));
            Sample s = new Sample(accelG, std, pressure);
            accSum = 0; accN = 0; gyroSum = 0; gyroSumSq = 0; gyroN = 0;
            return s;
        }
    }

    // --- Khác -----------------------------------------------------------------

    private final Runnable ticker = new Runnable() {
        @Override public void run() {
            long elapsed = SystemClock.elapsedRealtime() - startedElapsedMs;
            double sensorHz = 0.0;
            if (sensorEvents > 1 && lastSensorNs > firstSensorNs) {
                sensorHz = (sensorEvents - 1) * 1_000_000_000.0 / (lastSensorNs - firstSensorNs);
            }
            log("tick", "elapsed_ms=" + elapsed
                    + ",advertising=" + advertisingStarted
                    + ",scanning=" + scanningStarted
                    + ",scan_callbacks=" + scanCallbacks
                    + ",valid_frames=" + validProtocolFrames
                    + ",messages_issued=" + messagesIssued
                    + ",queue_unsent=" + queue.unsentCount()
                    + ",sensor_hz=" + String.format(Locale.US, "%.3f", sensorHz));
            updateUiStatus();
            // Tự giám sát Bluetooth: node cứu hộ không được nằm im khi BT bật/tắt
            BluetoothManager manager = getSystemService(BluetoothManager.class);
            BluetoothAdapter adapter = manager == null ? null : manager.getAdapter();
            boolean up = adapter != null && adapter.isEnabled();
            boolean probeRunning = advertiser != null || scanner != null;
            if (up && !probeRunning && !bluetoothProbeStarting) {
                log("bluetooth", "auto_restart=true");
                startBluetoothProbe();
            } else if (!up && probeRunning) {
                log("bluetooth", "adapter_lost,stopping_probe");
                stopBluetoothProbe();
            }
            handler.postDelayed(this, 10_000L);
        }
    };

    /** Dọn dẹp probe BLE (adapter tắt giữa chừng) — giữ service và cảm biến sống. */
    private void stopBluetoothProbe() {
        if (advertiser != null && legacyAdvertising) {
            try { advertiser.stopAdvertising(legacyAdvertiseCallback); } catch (Exception ignored) {}
        } else if (advertiser != null && advertisingSet != null) {
            try { advertiser.stopAdvertisingSet(advertiseCallback); } catch (Exception ignored) {}
        }
        if (scanner != null) {
            try { scanner.stopScan(scanCallback); } catch (Exception ignored) {}
        }
        advertiser = null;
        advertisingSet = null;
        scanner = null;
        advertisingStarted = false;
        scanningStarted = false;
        bluetoothProbeStarting = false;
    }

    private void notifyText(String title, String text) {
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm != null) nm.notify(NOTIFICATION_ID + 1, buildNotification(title + " — " + text));
    }

    private Notification buildNotification(String text) {
        return new Notification.Builder(this, CHANNEL)
                .setContentTitle("RescueSOS-Phone")
                .setContentText(text)
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setOngoing(true)
                .build();
    }

    private void logCapabilities() {
        BluetoothManager manager = getSystemService(BluetoothManager.class);
        BluetoothAdapter adapter = manager == null ? null : manager.getAdapter();
        String bluetooth = adapter == null ? "adapter=false" :
                "adapter=true,enabled=" + adapter.isEnabled()
                + ",multi_adv=" + adapter.isMultipleAdvertisementSupported();
        log("capability", "model=" + Build.MANUFACTURER + " " + Build.MODEL
                + ",sdk=" + Build.VERSION.SDK_INT + "," + bluetooth);
    }

    private boolean hasBluetoothPermissions() {
        if (Build.VERSION.SDK_INT < 31) return true;
        return checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED
                && checkSelfPermission(Manifest.permission.BLUETOOTH_ADVERTISE) == PackageManager.PERMISSION_GRANTED
                && checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED;
    }

    private void createNotificationChannel() {
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm != null) {
            nm.createNotificationChannel(new NotificationChannel(
                    CHANNEL, "RescueSOS-Phone", NotificationManager.IMPORTANCE_LOW));
        }
    }

    private static void log(String event, String fields) {
        Log.i(TAG, "event=" + event + "," + fields);
    }

    private static org.json.JSONObject frameFields(SosRecord rec, String extraKey, String extraVal) {
        org.json.JSONObject o = rec.toJson();
        try { o.put(extraKey, extraVal); } catch (Exception ignored) {}
        return o;
    }
}
