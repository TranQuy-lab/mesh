package org.rescuemesh.g0;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public final class SosCodecSelfTest {
    private static final byte[] KEY = "device-key-for-tests".getBytes(StandardCharsets.UTF_8);
    private static final String GOLDEN = "46f72a89abcdef399de83fcb3d2d53bc4c1ba811078a6028";

    public static void main(String[] args) {
        byte[] frame = pack(42);
        require(GOLDEN.equals(SosCodec.toHex(frame)), "golden mismatch: " + SosCodec.toHex(frame));
        require(SosCodec.verify(frame, KEY), "valid frame rejected");

        byte[] next = pack(43);
        require(!Arrays.equals(frame, next), "sequence did not change frame");
        require(SosCodec.verify(next, KEY), "next sequence rejected");

        byte[] relayed = frame.clone();
        relayed[1] = (byte) 0xe6;
        require(SosCodec.verify(relayed, KEY), "documented route rewrite rejected");

        byte[] tampered = frame.clone();
        tampered[8] ^= 1;
        require(!SosCodec.verify(tampered, KEY), "tamper accepted");
        System.out.println("4/4 Java SOS codec tests passed");
    }

    private static byte[] pack(int seq) {
        return SosCodec.packSos(0x89abcdefL, 12345, 21.028511, 105.804817,
                1, 2, 3, 11, 3, 0, 7, 15, seq, KEY);
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
