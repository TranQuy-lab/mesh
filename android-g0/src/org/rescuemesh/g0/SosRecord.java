package org.rescuemesh.g0;

import org.json.JSONObject;

/** Bản giải mã khung SOS v1 — ánh xạ trường trùng khớp rescuemesh/packets.py. */
public final class SosRecord {
    public final int ver, type, prio, encrypted;
    public final int ttl, hop, seq;
    public final long srcId;
    public final int timeMinutes;
    public final double lat, lon;
    public final int trigger, people, need, battery, gpsFix, moving;
    public final String frameId;

    private SosRecord(int ver, int type, int prio, int encrypted, int ttl, int hop, int seq,
                      long srcId, int timeMinutes, double lat, double lon,
                      int trigger, int people, int need, int battery, int gpsFix, int moving,
                      String frameId) {
        this.ver = ver; this.type = type; this.prio = prio; this.encrypted = encrypted;
        this.ttl = ttl; this.hop = hop; this.seq = seq;
        this.srcId = srcId; this.timeMinutes = timeMinutes;
        this.lat = lat; this.lon = lon;
        this.trigger = trigger; this.people = people; this.need = need;
        this.battery = battery; this.gpsFix = gpsFix; this.moving = moving;
        this.frameId = frameId;
    }

    /** Gọi sau khi SosCodec.verify() trả true. */
    public static SosRecord unpack(byte[] f) {
        if (f == null || f.length != SosCodec.SIZE) return null;
        int ver = (f[0] >>> 6) & 3;
        int type = (f[0] >>> 3) & 7;
        int prio = (f[0] >>> 1) & 3;
        int encrypted = f[0] & 1;
        int ttl = (f[1] >>> 4) & 15;
        int hop = f[1] & 15;
        int seq = f[2] & 0xff;
        long srcId = ((f[3] & 0xffL) << 24) | ((f[4] & 0xffL) << 16)
                | ((f[5] & 0xffL) << 8) | (f[6] & 0xffL);
        int minutes = f[7] & 0xff;
        double lat = decodeCoord(u24(f, 8), -90.0, 90.0);
        double lon = decodeCoord(u24(f, 11), -180.0, 180.0);
        int trigger = (f[14] >>> 6) & 3;
        int people = (f[14] >>> 3) & 7;
        int need = f[14] & 7;
        int battery = (f[15] >>> 4) & 15;
        int gpsFix = (f[15] >>> 2) & 3;
        int moving = (f[15] >>> 1) & 1;
        String frameId = SosCodec.toHex(f);
        return new SosRecord(ver, type, prio, encrypted, ttl, hop, seq, srcId, minutes,
                lat, lon, trigger, people, need, battery, gpsFix, moving, frameId);
    }

    public JSONObject toJson() {
        JSONObject o = new JSONObject();
        try {
            o.put("source", String.format("0x%08x", srcId));
            o.put("sequence", seq);
            o.put("hop", hop);
            o.put("ttl", ttl);
            o.put("latitude", Math.round(lat * 1e6) / 1e6);
            o.put("longitude", Math.round(lon * 1e6) / 1e6);
            o.put("trigger", trigger);
            o.put("people", people);
            o.put("need", need);
            o.put("battery", battery);
            o.put("gps_fix", gpsFix);
            o.put("moving", moving);
            o.put("frame_id", frameId);
        } catch (Exception ignored) {}
        return o;
    }

    private static int u24(byte[] f, int off) {
        return ((f[off] & 0xff) << 16) | ((f[off + 1] & 0xff) << 8) | (f[off + 2] & 0xff);
    }

    private static double decodeCoord(int raw, double min, double max) {
        return min + raw * (max - min) / (double) ((1 << 24) - 1);
    }
}
