/** Tab La bàn — mũi tên chỉ tới SOS đang chọn (bearing − hướng máy), khoảng cách lớn. */
import { StyleSheet, Text, View } from "react-native";

import { palette, radius, spacing, triggerColor, triggerLabel, type } from "@/constants/theme";
import { bearingDegrees, distanceMeters, octant } from "@/lib/api";
import { useSosStore } from "@/lib/store";

export default function CompassScreen() {
  const { sos, selected, own, heading } = useSosStore();
  const target = sos.find((s) => s.source === selected) ?? sos[0] ?? null;

  const hasCoords = target && target.latitude != null && target.longitude != null && own;
  const dist = hasCoords
    ? distanceMeters([own.lat, own.lon], [target.latitude as number, target.longitude as number])
    : null;
  const bearing = hasCoords
    ? bearingDegrees([own.lat, own.lon], [target.latitude as number, target.longitude as number])
    : null;
  const arrowAngle = bearing != null && heading != null ? bearing - heading : bearing ?? 0;

  return (
    <View style={styles.flex}>
      <Text style={styles.heading}>
        {target ? `SOS ${target.source}` : "Chưa chọn SOS"}
      </Text>

      <View style={styles.dial}>
        <Text style={styles.dialN}>B</Text>
        <Text style={[styles.dialMark, styles.dialE]}>Đ</Text>
        <Text style={[styles.dialMark, styles.dialS]}>N</Text>
        <Text style={[styles.dialMark, styles.dialW]}>T</Text>
        <View style={[styles.arrow, { transform: [{ rotate: `${arrowAngle}deg` }] }]}>
          <Text style={[styles.arrowGlyph, { color: target ? triggerColor[target.trigger] ?? palette.sos : palette.textDim }]}>
            ▲
          </Text>
        </View>
      </View>

      {hasCoords && (
        <Text style={styles.distance}>
          {dist! >= 1000 ? `${(dist! / 1000).toFixed(1)} km` : `${Math.round(dist!)} m`}
        </Text>
      )}
      {bearing != null && (
        <Text style={styles.octantText}>
          hướng {octant(bearing)} ({Math.round(bearing)}°){heading != null ? ` • máy đang ${Math.round(heading)}°` : ""}
        </Text>
      )}
      {!hasCoords && (
        <Text style={styles.hint}>
          SOS này chưa có toạ độ (máy nạn nhân mất GPS) hoặc máy cứu hộ chưa có vị trí —
          bật Vị trí và thử lại.
        </Text>
      )}

      {target && (
        <Text style={styles.meta}>
          {triggerLabel[target.trigger] ?? "?"} • hop {target.hop ?? "?"} • pin{" "}
          {target.battery != null ? `${target.battery}/15` : "?"} • cập nhật {target.age_s}s trước
        </Text>
      )}
      <Text style={styles.hintSmall}>
        Chọn SOS khác ở tab SOS; ghim trên bản đồ cũng đặt mục tiêu la bàn.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: palette.bg, alignItems: "center", paddingTop: spacing.xl, paddingHorizontal: spacing.l },
  heading: { ...type.heading, color: palette.text },
  dial: {
    width: 280,
    height: 280,
    borderRadius: 140,
    borderWidth: 2,
    borderColor: palette.border,
    backgroundColor: palette.surface,
    alignItems: "center",
    justifyContent: "center",
    marginTop: spacing.l,
  },
  dialN: { position: "absolute", top: 10, color: palette.textDim, fontSize: 16, fontWeight: "700" },
  dialMark: { color: palette.textDim, fontSize: 16 },
  dialS: { position: "absolute", bottom: 10, color: palette.textDim, fontSize: 16 },
  dialE: { position: "absolute", right: 12, color: palette.textDim, fontSize: 16 },
  dialW: { position: "absolute", left: 12, color: palette.textDim, fontSize: 16 },
  arrow: { alignItems: "center", justifyContent: "center" },
  arrowGlyph: { fontSize: 110, lineHeight: 130 },
  distance: { ...type.big, color: palette.text, marginTop: spacing.l },
  octantText: { ...type.body, color: palette.textDim, marginTop: spacing.xs },
  meta: { ...type.small, color: palette.textDim, marginTop: spacing.m },
  hint: { ...type.small, color: palette.textDim, textAlign: "center", marginTop: spacing.m },
  hintSmall: { ...type.small, color: palette.textDim, opacity: 0.7, textAlign: "center", marginTop: spacing.s },
});
