package org.rescuemesh.g0;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.security.GeneralSecurityException;
import java.security.MessageDigest;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

/** Pure-Java codec for the 24-byte RescueMesh SOS v1 frame. */
public final class SosCodec {
    public static final int SIZE = 24;
    public static final int TAG_BYTES = 8;
    private static final int COORD_MAX = (1 << 24) - 1;

    private SosCodec() {}

    public static byte[] packSos(long srcId, long timeMinutes, double lat, double lon,
                                 int trigger, int people, int need, int battery,
                                 int gpsFix, int moving, int hop, int ttl, int seq,
                                 byte[] key) {
        check(srcId, 32, "srcId");
        check(trigger, 2, "trigger");
        check(people, 3, "people");
        check(need, 3, "need");
        check(battery, 4, "battery");
        check(gpsFix, 2, "gpsFix");
        check(moving, 1, "moving");
        check(hop, 4, "hop");
        check(ttl, 4, "ttl");
        check(seq, 8, "seq");
        if (key == null || key.length == 0) throw new IllegalArgumentException("empty key");

        byte[] prefix = new byte[SIZE - TAG_BYTES];
        prefix[0] = (byte) ((1 << 6) | (3 << 1)); // ver=1, type=SOS, prio=3
        prefix[1] = (byte) ((ttl << 4) | hop);
        prefix[2] = (byte) seq;
        ByteBuffer.wrap(prefix, 3, 4).order(ByteOrder.BIG_ENDIAN).putInt((int) srcId);
        prefix[7] = (byte) timeMinutes;
        putU24(prefix, 8, encodeCoord(lat, -90.0, 90.0));
        putU24(prefix, 11, encodeCoord(lon, -180.0, 180.0));
        prefix[14] = (byte) ((trigger << 6) | (people << 3) | need);
        prefix[15] = (byte) ((battery << 4) | (gpsFix << 2) | (moving << 1));

        byte[] authenticated = new byte[prefix.length - 1];
        authenticated[0] = prefix[0];
        System.arraycopy(prefix, 2, authenticated, 1, prefix.length - 2);
        byte[] tag = hmac64(key, authenticated);
        byte[] frame = new byte[SIZE];
        System.arraycopy(prefix, 0, frame, 0, prefix.length);
        System.arraycopy(tag, 0, frame, prefix.length, TAG_BYTES);
        return frame;
    }

    public static boolean verify(byte[] frame, byte[] key) {
        if (frame == null || frame.length != SIZE || key == null || key.length == 0) return false;
        byte[] authenticated = new byte[SIZE - TAG_BYTES - 1];
        authenticated[0] = frame[0];
        System.arraycopy(frame, 2, authenticated, 1, SIZE - TAG_BYTES - 2);
        byte[] expected = hmac64(key, authenticated);
        byte[] actual = new byte[TAG_BYTES];
        System.arraycopy(frame, SIZE - TAG_BYTES, actual, 0, TAG_BYTES);
        return MessageDigest.isEqual(expected, actual);
    }

    public static String toHex(byte[] value) {
        StringBuilder out = new StringBuilder(value.length * 2);
        for (byte b : value) out.append(String.format("%02x", b & 0xff));
        return out.toString();
    }

    private static int encodeCoord(double degrees, double min, double max) {
        if (!Double.isFinite(degrees) || degrees < min || degrees > max) {
            throw new IllegalArgumentException("coordinate out of range");
        }
        return (int) Math.round((degrees - min) / (max - min) * COORD_MAX);
    }

    private static void putU24(byte[] out, int offset, int value) {
        out[offset] = (byte) (value >>> 16);
        out[offset + 1] = (byte) (value >>> 8);
        out[offset + 2] = (byte) value;
    }

    private static byte[] hmac64(byte[] key, byte[] data) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(key, "HmacSHA256"));
            byte[] full = mac.doFinal(data);
            byte[] truncated = new byte[TAG_BYTES];
            System.arraycopy(full, 0, truncated, 0, TAG_BYTES);
            return truncated;
        } catch (GeneralSecurityException error) {
            throw new IllegalStateException("HmacSHA256 unavailable", error);
        }
    }

    private static void check(long value, int bits, String name) {
        long max = bits == 32 ? 0xffff_ffffL : (1L << bits) - 1;
        if (value < 0 || value > max) throw new IllegalArgumentException(name + " out of range");
    }
}
