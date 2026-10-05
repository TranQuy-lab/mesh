/** Tab SOS — danh sách SOS đang hoạt động; chạm để đặt mục tiêu la bàn. */
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";

import { palette, radius, spacing, triggerColor, triggerLabel, type } from "@/constants/theme";
import { bearingDegrees, distanceMeters, octant } from "@/lib/api";
import { useSosStore } from "@/lib/store";

export default function SosScreen() {
  const { sos, selected, setSelected, own, status, error, lastRefresh, refresh } = useSosStore();

  return (
    <View style={styles.flex}>
      <View style={styles.statusBar}>
        <View style={[styles.dot, { backgroundColor: status === "ok" ? palette.safe : status === "error" ? palette.sos : palette.textDim }]} />
        <Text style={styles.statusText}>
          {status === "ok"
            ? `Kết nối server • ${sos.length} SOS • ${lastRefresh ? new Date(lastRefresh).toLocaleTimeString() : ""}`
            : status === "error"
              ? `Lỗi server: ${error ?? "?"}`
              : "Đang kết nối…"}
        </Text>
        <Pressable onPress={() => refresh()} hitSlop={8}>
          <Text style={styles.refresh}>Làm mới</Text>
        </Pressable>
      </View>

      <FlatList
        data={sos}
        keyExtractor={(s) => s.source + s.sequence}
        contentContainerStyle={{ padding: spacing.m, gap: spacing.s }}
        ListEmptyComponent={
          <Text style={styles.empty}>
            Chưa có SOS nào. Node nạn nhân phát SOS sẽ hiện ở đây trong ~5 giây.
          </Text>
        }
        renderItem={({ item }) => {
          const hasPos = own && item.latitude != null && item.longitude != null;
          const dist = hasPos
            ? distanceMeters([own.lat, own.lon], [item.latitude as number, item.longitude as number])
            : null;
          const bearing = hasPos
            ? bearingDegrees([own.lat, own.lon], [item.latitude as number, item.longitude as number])
            : null;
          const isSel = selected === item.source;
          return (
            <Pressable
              onPress={() => setSelected(isSel ? null : item.source)}
              style={[styles.card, isSel && { borderColor: palette.sos }]}
            >
              <View style={[styles.cardDot, { backgroundColor: triggerColor[item.trigger] ?? palette.manual }]} />
              <View style={styles.cardBody}>
                <Text style={styles.cardTitle}>
                  {item.source} {isSel ? "• đang theo" : ""}
                </Text>
                <Text style={styles.cardLine}>
                  {triggerLabel[item.trigger] ?? "?"} • hop {item.hop ?? "?"} • pin{" "}
                  {item.battery != null ? `${item.battery}/15` : "?"} • GPS cấp {item.gps_fix ?? 0}
                </Text>
                <Text style={styles.cardDim}>
                  {dist != null
                    ? `${dist >= 1000 ? (dist / 1000).toFixed(1) + " km" : Math.round(dist) + " m"} • hướng ${octant(bearing as number)} • `
                    : ""}
                  {item.age_s}s trước • {item.frames} khung
                </Text>
              </View>
            </Pressable>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: palette.bg },
  statusBar: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.s,
    paddingHorizontal: spacing.m,
    paddingVertical: spacing.s,
    borderBottomWidth: 1,
    borderBottomColor: palette.border,
  },
  dot: { width: 10, height: 10, borderRadius: 5 },
  statusText: { ...type.small, color: palette.textDim, flex: 1 },
  refresh: { ...type.small, color: palette.link },
  empty: { ...type.body, color: palette.textDim, textAlign: "center", marginTop: spacing.xl },
  card: {
    flexDirection: "row",
    gap: spacing.m,
    backgroundColor: palette.surface,
    borderColor: palette.border,
    borderWidth: 1,
    borderRadius: radius.m,
    padding: spacing.m,
  },
  cardDot: { width: 14, height: 14, borderRadius: 7, marginTop: 4 },
  cardBody: { flex: 1, gap: 2 },
  cardTitle: { ...type.heading, color: palette.text },
  cardLine: { ...type.body, color: palette.text },
  cardDim: { ...type.small, color: palette.textDim },
});
