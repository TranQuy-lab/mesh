package org.rescuemesh.g0;

import android.content.Context;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/**
 * Hàng đợi SOS bền trên đĩa — "lưu–mang–tiếp" sống qua restart (RQ3, H3):
 * pending.jsonl giữ khung chưa đẩy ra ngoài; seen.txt giữ ID khung đã gặp
 * (vòng 4096) để chống trùng sau khi máy khởi động lại.
 */
public final class SosQueue {
    private static final int SEEN_MAX = 4096;

    private final File pendingFile;
    private final File seenFile;
    private final List<JSONObject> pending = new ArrayList<>();
    private final Set<String> seen = new LinkedHashSet<>();

    public SosQueue(Context context) {
        File dir = new File(context.getFilesDir(), "sos");
        dir.mkdirs();
        pendingFile = new File(dir, "pending.jsonl");
        seenFile = new File(dir, "seen.txt");
        load();
    }

    public synchronized boolean addReceived(byte[] frame, long nowMs) {
        String frameId = SosCodec.toHex(frame);
        if (!seen.add(frameId)) return false;
        trimSeen();
        appendSeen(frameId);
        SosRecord rec = SosRecord.unpack(frame);
        JSONObject o = rec.toJson();
        try {
            o.put("origin", "rx");
            o.put("frame_hex", frameId);
            o.put("first_seen_ms", nowMs);
            o.put("sent_out", false);
        } catch (Exception ignored) {}
        pending.add(o);
        rewritePending();
        return true;
    }

    public synchronized void addOwn(byte[] frame, long nowMs) {
        SosRecord rec = SosRecord.unpack(frame);
        JSONObject o = rec.toJson();
        try {
            o.put("origin", "own");
            o.put("frame_hex", SosCodec.toHex(frame));
            o.put("first_seen_ms", nowMs);
            o.put("sent_out", false);
        } catch (Exception ignored) {}
        pending.add(o);
        rewritePending();
    }

    public synchronized List<JSONObject> takeUnsent(int limit) {
        List<JSONObject> out = new ArrayList<>();
        for (JSONObject o : pending) {
            if (out.size() >= limit) break;
            if (!o.optBoolean("sent_out", false)) out.add(o);
        }
        return out;
    }

    public synchronized int unsentCount() {
        int n = 0;
        for (JSONObject o : pending) if (!o.optBoolean("sent_out", false)) n++;
        return n;
    }

    public synchronized void markSent(String frameId, String via) {
        for (JSONObject o : pending) {
            if (frameId.equals(o.optString("frame_id")) && !o.optBoolean("sent_out")) {
                try {
                    o.put("sent_out", true);
                    o.put("sent_via", via);
                } catch (Exception ignored) {}
            }
        }
        rewritePending();
    }

    public synchronized int size() { return pending.size(); }

    private void load() {
        readLines(pendingFile, line -> {
            try { pending.add(new JSONObject(line)); } catch (Exception ignored) {}
        });
        readLines(seenFile, line -> {
            if (!line.isEmpty()) seen.add(line);
        });
    }

    private interface LineFn { void accept(String line); }

    private static void readLines(File f, LineFn fn) {
        if (!f.exists()) return;
        try (InputStreamReader r = new InputStreamReader(new FileInputStream(f), StandardCharsets.UTF_8)) {
            StringBuilder sb = new StringBuilder();
            int c;
            while ((c = r.read()) != -1) {
                if (c == '\n') { fn.accept(sb.toString()); sb.setLength(0); }
                else sb.append((char) c);
            }
            if (sb.length() > 0) fn.accept(sb.toString());
        } catch (Exception ignored) {}
    }

    private void trimSeen() {
        while (seen.size() > SEEN_MAX) {
            java.util.Iterator<String> it = seen.iterator();
            it.next();
            it.remove();
        }
    }

    private void appendSeen(String frameId) {
        try (OutputStreamWriter w = new OutputStreamWriter(
                new FileOutputStream(seenFile, true), StandardCharsets.UTF_8)) {
            w.write(frameId + "\n");
        } catch (Exception ignored) {}
    }

    private void rewritePending() {
        try (OutputStreamWriter w = new OutputStreamWriter(
                new FileOutputStream(pendingFile, false), StandardCharsets.UTF_8)) {
            for (JSONObject o : pending) w.write(o.toString() + "\n");
        } catch (Exception ignored) {}
    }

    /** JSON cho cổng ra: mảng khung chưa gửi. */
    public static JSONArray toJson(List<JSONObject> records) {
        JSONArray arr = new JSONArray();
        for (JSONObject o : records) arr.put(o);
        return arr;
    }
}
