/** Tab Cấu hình — địa chỉ server SOS, kiểm kết nối; giải thích vai trò app. */
import { useEffect, useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";

import { palette, radius, spacing, type } from "@/constants/theme";
import { useSosStore } from "@/lib/store";

export default function SettingsScreen() {
  const { serverUrl, setServerUrl, refresh, status, error } = useSosStore();
  const [draft, setDraft] = useState(serverUrl);
  const [saved, setSaved] = useState(false);

  useEffect(() => setDraft(serverUrl), [serverUrl]);

  return (
    <View style={styles.flex}>
      <Text style={styles.heading}>Server SOS (khâu ④)</Text>
      <TextInput
        value={draft}
        onChangeText={setDraft}
        placeholder="http://192.168.1.10:8787"
        placeholderTextColor={palette.textDim}
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="url"
        style={styles.input}
      />
      <Pressable
        style={styles.saveBtn}
        onPress={async () => {
          await setServerUrl(draft);
          setSaved(true);
          setTimeout(() => setSaved(false), 2000);
          refresh();
        }}
      >
        <Text style={styles.saveText}>{saved ? "Đã lưu ✓" : "Lưu và kiểm tra"}</Text>
      </Pressable>

      <View style={styles.statusRow}>
        <View style={[styles.dot, { backgroundColor: status === "ok" ? palette.safe : status === "error" ? palette.sos : palette.textDim }]} />
        <Text style={styles.statusText}>
          {status === "ok" ? "Server trả lời bình thường" : status === "error" ? `Không kết nối được: ${error ?? "?"}` : "Chưa kiểm tra"}
        </Text>
      </View>

      <Text style={styles.tip}>
        Cùng mạng WiFi với laptop chạy server thì dùng IP LAN; dây USB thì dùng
        {" "}
        <Text style={styles.mono}>adb reverse tcp:8787 tcp:8787</Text> và để nguyên
        {" "}
        <Text style={styles.mono}>http://127.0.0.1:8787</Text>.
      </Text>

      <Text style={styles.about}>
        RescueSOS Console là app phía cứu hộ: xem bản đồ SOS, la bàn chỉ đường, danh
        sách ưu tiên. Phát/nhảy SOS BLE do app node riêng đảm nhiệm (tiết kiệm pin,
        chạy nền bền) — Console chỉ đọc server.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: palette.bg, padding: spacing.l, gap: spacing.m },
  heading: { ...type.heading, color: palette.text },
  input: {
    backgroundColor: palette.surface,
    borderColor: palette.border,
    borderWidth: 1,
    borderRadius: radius.s,
    color: palette.text,
    padding: spacing.m,
    fontSize: 15,
  },
  saveBtn: {
    backgroundColor: palette.sos,
    borderRadius: radius.s,
    alignItems: "center",
    padding: spacing.m,
  },
  saveText: { color: "#fff", fontWeight: "700", fontSize: 15 },
  statusRow: { flexDirection: "row", alignItems: "center", gap: spacing.s },
  dot: { width: 10, height: 10, borderRadius: 5 },
  statusText: { ...type.small, color: palette.textDim, flex: 1 },
  tip: { ...type.small, color: palette.textDim, lineHeight: 20 },
  mono: { fontFamily: "monospace" },
  about: { ...type.small, color: palette.textDim, lineHeight: 20, marginTop: spacing.s },
});
