package org.rescuemesh.g0;

import android.content.Context;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

/** Nhật ký sự kiện JSONL (drill RQ3/RQ4): t_ms, event, các trường kèm. */
public final class EventLog {
    private final File file;
    private final long bootMs = System.currentTimeMillis();

    public EventLog(Context context) {
        file = new File(context.getExternalFilesDir(null), "events.jsonl");
    }

    public synchronized void write(String event, JSONObject fields) {
        try (OutputStreamWriter w = new OutputStreamWriter(
                new FileOutputStream(file, true), StandardCharsets.UTF_8)) {
            JSONObject o = fields == null ? new JSONObject() : fields;
            o.put("event", event);
            o.put("wall_ms", bootMs);
            w.write(o.toString() + "\n");
        } catch (Exception ignored) {}
    }

    public static JSONObject fields(String... kv) {
        JSONObject o = new JSONObject();
        for (int i = 0; i + 1 < kv.length; i += 2) {
            try { o.put(kv[i], kv[i + 1]); } catch (Exception ignored) {}
        }
        return o;
    }
}
