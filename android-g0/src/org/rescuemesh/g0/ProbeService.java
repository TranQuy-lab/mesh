package org.rescuemesh.g0;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.AdvertiseData;
import android.bluetooth.le.AdvertisingSet;
import android.bluetooth.le.AdvertisingSetCallback;
import android.bluetooth.le.AdvertisingSetParameters;
import android.bluetooth.le.BluetoothLeAdvertiser;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.SystemClock;
import android.provider.Settings;
import android.util.Log;

import java.util.HashSet;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.nio.charset.StandardCharsets;

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

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Set<String> devices = new HashSet<>();
    private final Set<Integer> messageIds = new HashSet<>();
    private final Set<String> seenFrames = new HashSet<>();
    private long startedElapsedMs;
    private long scanCallbacks;
    private long goldenMatches;
    private long validProtocolFrames;
    private long messagesIssued;
    private long sensorEvents;
    private long firstSensorNs;
    private long lastSensorNs;
    private boolean advertisingStarted;
    private boolean scanningStarted;
    private long localSourceId = 0x89abcdefL;

    private BluetoothLeAdvertiser advertiser;
    private AdvertisingSet advertisingSet;
    private BluetoothLeScanner scanner;
    private SensorManager sensorManager;
    private Sensor accelerometer;

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
                    + ",connectable=false,payload_bytes=" + SOS_GOLDEN.length
                    + ",messages_issued=" + messagesIssued);
            handler.postDelayed(rotateMessage, 1_000L);
        }

        @Override public void onAdvertisingDataSet(AdvertisingSet set, int status) {
            if (status != ADVERTISE_SUCCESS) {
                log("advertise_data", "ok=false,error=" + status
                        + ",messages_issued=" + messagesIssued);
            }
        }
    };

    private final Runnable rotateMessage = new Runnable() {
        @Override public void run() {
            if (advertisingSet == null) return;
            int seq = (42 + (int) messagesIssued) & 0xff;
            long minute = 12345 + messagesIssued / 60;
            byte[] frame = SosCodec.packSos(localSourceId, minute, 21.028511, 105.804817,
                    1, 2, 3, 11, 3, 0, 7, 15, seq, DEVICE_KEY);
            advertisingSet.setAdvertisingData(advertiseData(frame));
            messagesIssued++;
            handler.postDelayed(this, 1_000L);
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
                int messageId = ((manufacturerData[3] & 0xff) << 24)
                        | ((manufacturerData[4] & 0xff) << 16)
                        | ((manufacturerData[5] & 0xff) << 8)
                        | (manufacturerData[6] & 0xff);
                messageIds.add(messageId);
                String frameId = SosCodec.toHex(manufacturerData);
                if ((manufacturerData[3] & 0xff) != ((localSourceId >>> 24) & 0xff)
                        || (manufacturerData[4] & 0xff) != ((localSourceId >>> 16) & 0xff)
                        || (manufacturerData[5] & 0xff) != ((localSourceId >>> 8) & 0xff)
                        || (manufacturerData[6] & 0xff) != (localSourceId & 0xff)) {
                    if (seenFrames.add(frameId)) relay(manufacturerData);
                }
            }
            if (Arrays.equals(SOS_GOLDEN, manufacturerData)) {
                goldenMatches++;
                if (goldenMatches <= 3) {
                    log("golden_rx", "match=" + goldenMatches
                            + ",payload_bytes=" + manufacturerData.length);
                }
            }
            String address = "redacted";
            try {
                if (result.getDevice() != null) {
                    address = Integer.toHexString(result.getDevice().getAddress().hashCode());
                }
            } catch (SecurityException ignored) {}
            devices.add(address);
        }

        @Override public void onBatchScanResults(List<ScanResult> results) {
            scanCallbacks += results.size();
            for (ScanResult result : results) onScanResult(0, result);
        }

        @Override public void onScanFailed(int errorCode) {
            scanningStarted = false;
            log("scan_start", "ok=false,error=" + errorCode);
        }
    };

    private final Runnable ticker = new Runnable() {
        @Override public void run() {
            long elapsed = SystemClock.elapsedRealtime() - startedElapsedMs;
            double sensorHz = 0.0;
            if (sensorEvents > 1 && lastSensorNs > firstSensorNs) {
                sensorHz = (sensorEvents - 1) * 1_000_000_000.0 / (lastSensorNs - firstSensorNs);
            }
            log("tick", "elapsed_ms=" + elapsed
                    + ",screen_interactive=" + isInteractive()
                    + ",advertising=" + advertisingStarted
                    + ",scanning=" + scanningStarted
                    + ",scan_callbacks=" + scanCallbacks
                    + ",golden_matches=" + goldenMatches
                    + ",valid_frames=" + validProtocolFrames
                    + ",unique_messages=" + messageIds.size()
                    + ",messages_issued=" + messagesIssued
                    + ",unique_devices=" + devices.size()
                    + ",sensor_events=" + sensorEvents
                    + ",sensor_hz=" + String.format(Locale.US, "%.3f", sensorHz));
            handler.postDelayed(this, 10_000L);
        }
    };

    @Override public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        Notification notification = new Notification.Builder(this, CHANNEL)
                .setContentTitle("RescueMesh G0 đang đo")
                .setContentText("BLE advertising + scan + accelerometer 20 Hz")
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setOngoing(true)
                .build();
        startForeground(NOTIFICATION_ID, notification);
        startedElapsedMs = SystemClock.elapsedRealtime();
        localSourceId = localSourceId();
        log("codec_selftest", "golden=" + SOS_GOLDEN_HEX.equals(SosCodec.toHex(SOS_GOLDEN))
                + ",verify=" + SosCodec.verify(SOS_GOLDEN, DEVICE_KEY)
                + ",actual=" + SosCodec.toHex(SOS_GOLDEN));
        logCapabilities();
        startSensorProbe();
        handler.post(ticker);
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        String advertiseMode = intent == null ? null : intent.getStringExtra("advertise_mode");
        String scanMode = intent == null ? null : intent.getStringExtra("scan_mode");
        startBluetoothProbe(advertiseMode, scanMode);
        return START_STICKY;
    }

    @Override public void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        if (advertiser != null && advertisingSet != null) {
            try { advertiser.stopAdvertisingSet(advertiseCallback); } catch (Exception ignored) {}
        }
        if (scanner != null) {
            try { scanner.stopScan(scanCallback); } catch (Exception ignored) {}
        }
        if (sensorManager != null) sensorManager.unregisterListener(this);
        log("stop", "elapsed_ms=" + (SystemClock.elapsedRealtime() - startedElapsedMs));
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) { return null; }

    @Override public void onSensorChanged(SensorEvent event) {
        sensorEvents++;
        if (firstSensorNs == 0) firstSensorNs = event.timestamp;
        lastSensorNs = event.timestamp;
    }

    @Override public void onAccuracyChanged(Sensor sensor, int accuracy) {}

    private void logCapabilities() {
        BluetoothManager manager = getSystemService(BluetoothManager.class);
        BluetoothAdapter adapter = manager == null ? null : manager.getAdapter();
        String bluetooth = adapter == null ? "adapter=false" :
                "adapter=true,enabled=" + adapter.isEnabled()
                + ",multi_adv=" + adapter.isMultipleAdvertisementSupported()
                + ",offloaded_filter=" + adapter.isOffloadedFilteringSupported()
                + ",offloaded_batch=" + adapter.isOffloadedScanBatchingSupported()
                + ",extended_adv=" + adapter.isLeExtendedAdvertisingSupported()
                + ",max_adv_data=" + adapter.getLeMaximumAdvertisingDataLength();
        log("capability", "model=" + Build.MANUFACTURER + " " + Build.MODEL
                + ",sdk=" + Build.VERSION.SDK_INT + "," + bluetooth);

        sensorManager = getSystemService(SensorManager.class);
        accelerometer = sensorManager == null ? null : sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        if (accelerometer != null) {
            log("accelerometer", "name=" + accelerometer.getName()
                    + ",vendor=" + accelerometer.getVendor()
                    + ",min_delay_us=" + accelerometer.getMinDelay()
                    + ",max_delay_us=" + accelerometer.getMaxDelay()
                    + ",fifo_max=" + accelerometer.getFifoMaxEventCount()
                    + ",fifo_reserved=" + accelerometer.getFifoReservedEventCount()
                    + ",power_ma=" + accelerometer.getPower()
                    + ",wakeup=" + accelerometer.isWakeUpSensor());
        }
    }

    private void startBluetoothProbe(String requestedAdvertiseMode, String requestedScanMode) {
        if (!hasBluetoothPermissions()) {
            log("permission", "bluetooth=false");
            return;
        }
        BluetoothManager manager = getSystemService(BluetoothManager.class);
        BluetoothAdapter adapter = manager == null ? null : manager.getAdapter();
        if (adapter == null || !adapter.isEnabled()) {
            log("bluetooth", "ready=false,reason=adapter_disabled");
            return;
        }
        advertiser = adapter.getBluetoothLeAdvertiser();
        scanner = adapter.getBluetoothLeScanner();

        String advertiseMode = "balanced".equals(requestedAdvertiseMode)
                ? "balanced" : "low_latency";
        String scanMode = "balanced".equals(requestedScanMode)
                ? "balanced" : "low_latency";

        if (advertiser == null) {
            log("advertise_start", "ok=false,error=advertiser_null");
        } else {
            int interval = "balanced".equals(advertiseMode)
                    ? AdvertisingSetParameters.INTERVAL_MEDIUM
                    : AdvertisingSetParameters.INTERVAL_LOW;
            AdvertisingSetParameters parameters = new AdvertisingSetParameters.Builder()
                    .setLegacyMode(true)
                    .setInterval(interval)
                    .setTxPowerLevel(AdvertisingSetParameters.TX_POWER_HIGH)
                    .setConnectable(false)
                    // A scannable legacy packet is received more consistently by
                    // BlueZ laptop adapters while the SOS payload remains in the
                    // primary advertisement; no GATT connection is required.
                    .setScannable(true)
                    .build();
            log("advertise_config", "mode=" + advertiseMode + ",interval_units=" + interval);
            try {
                advertiser.startAdvertisingSet(parameters, advertiseData(initialFrame()),
                        null, null, null, advertiseCallback);
            } catch (IllegalArgumentException error) {
                log("advertise_start", "ok=false,error=callback_busy");
            }
        }

        if (scanner == null) {
            log("scan_start", "ok=false,error=scanner_null");
        } else {
            ScanSettings settings = new ScanSettings.Builder()
                    .setScanMode("balanced".equals(scanMode)
                            ? ScanSettings.SCAN_MODE_BALANCED : ScanSettings.SCAN_MODE_LOW_LATENCY)
                    .setReportDelay(0)
                    .build();
            List<ScanFilter> filters = Arrays.asList(new ScanFilter.Builder()
                    .setManufacturerData(COMPANY_ID_LAB,
                            new byte[] {0x40}, new byte[] {(byte) 0xc0})
                    .build());
            try {
                scanner.startScan(filters, settings, scanCallback);
                scanningStarted = true;
                log("scan_start", "ok=true,mode=" + scanMode + ",filtered=true");
            } catch (IllegalArgumentException error) {
                log("scan_start", "ok=false,error=callback_busy");
            }
        }
    }

    /** Relay keeps the end-to-end MAC valid because byte 1 is route metadata. */
    private void relay(byte[] received) {
        if (advertisingSet == null || received.length != SosCodec.SIZE) return;
        int route = received[1] & 0xff;
        int ttl = (route >>> 4) & 0x0f;
        int hop = route & 0x0f;
        if (ttl == 0) return;
        byte[] forwarded = received.clone();
        forwarded[1] = (byte) (((ttl - 1) << 4) | Math.min(15, hop == 15 ? 0 : hop + 1));
        try { advertisingSet.setAdvertisingData(advertiseData(forwarded)); }
        catch (Exception error) { log("relay", "ok=false,error=" + error.getClass().getSimpleName()); }
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

    private byte[] initialFrame() {
        return SosCodec.packSos(localSourceId, 12345, 21.028511, 105.804817,
                1, 2, 3, 11, 3, 0, 7, 15, 42, DEVICE_KEY);
    }

    private void startSensorProbe() {
        if (sensorManager == null || accelerometer == null) {
            log("sensor_start", "ok=false");
            return;
        }
        boolean ok = sensorManager.registerListener(this, accelerometer, 50_000, 2_000_000);
        log("sensor_start", "ok=" + ok + ",period_us=50000,max_latency_us=2000000");
    }

    private boolean hasBluetoothPermissions() {
        if (Build.VERSION.SDK_INT < 31) return true;
        return checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED
                && checkSelfPermission(Manifest.permission.BLUETOOTH_ADVERTISE) == PackageManager.PERMISSION_GRANTED
                && checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED;
    }

    private boolean isInteractive() {
        android.os.PowerManager pm = getSystemService(android.os.PowerManager.class);
        return pm != null && pm.isInteractive();
    }

    private void createNotificationChannel() {
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm != null) {
            nm.createNotificationChannel(new NotificationChannel(
                    CHANNEL, "RescueMesh G0", NotificationManager.IMPORTANCE_LOW));
        }
    }

    private static void log(String event, String fields) {
        Log.i(TAG, "event=" + event + "," + fields);
    }

    private static byte[] hex(String value) {
        byte[] out = new byte[value.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(value.substring(i * 2, i * 2 + 2), 16);
        }
        return out;
    }
}
