/** Tab Bản đồ — MapLibre + tile OSM miễn phí (không API key), ghim SOS theo loại. */
import { useMemo, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { Camera, Map, Marker, UserLocation } from "@maplibre/maplibre-react-native";
import { useRouter } from "expo-router";
import { Host, BottomSheet, Column, Button } from "@expo/ui";

import { palette, radius, spacing, triggerColor, triggerLabel, type } from "@/constants/theme";
import { useSosStore } from "@/lib/store";
import type { SosItem } from "@/lib/api";

// Nền bản đồ: raster OSM (miễn phí, không đăng ký). Offline pack sẽ thêm sau drill.
const OSM_STYLE = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "© OpenStreetMap contributors",
    },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};

export default function MapScreen() {
  const { sos, own, selected, setSelected } = useSosStore();
  const router = useRouter();
  const [detail, setDetail] = useState<SosItem | null>(null);

  const withCoords = useMemo(() => sos.filter((s) => s.latitude != null && s.longitude != null), [sos]);
  const center = useMemo<[number, number]>(() => {
    if (own) return [own.lon, own.lat];
    if (withCoords[0]) return [withCoords[0].longitude as number, withCoords[0].latitude as number];
    return [105.8, 21.0]; // fallback: Hà Nội
  }, [own, withCoords]);

  return (
    <View style={styles.flex}>
      <Map mapStyle={OSM_STYLE as never} style={styles.flex}>
        <Camera initialViewState={{ center, zoom: own ? 15 : 12 }} />
        <UserLocation />
        {withCoords.map((s) => (
          <Marker
            key={s.source + s.sequence}
            lngLat={[s.longitude as number, s.latitude as number]}
            onPress={() => {
              setDetail(s);
              setSelected(s.source);
            }}
          >
            <View style={[styles.pin, { backgroundColor: triggerColor[s.trigger] ?? palette.manual }]}>
              <Text style={styles.pinText}>
                {s.trigger === 2 ? "!" : s.trigger === 3 ? "~" : "S"}
              </Text>
            </View>
          </Marker>
        ))}
      </Map>

      <View style={styles.legend} pointerEvents="none">
        <LegendDot color={palette.sos} label="Ngã" />
        <LegendDot color={palette.water} label="Chìm" />
        <LegendDot color={palette.manual} label="Tay" />
      </View>

      <Host>
        <BottomSheet
          isPresented={detail != null}
          onDismiss={() => setDetail(null)}
          snapPoints={["half", "full"]}
        >
          <Column style={styles.sheet}>
            <Text style={styles.sheetTitle}>
              SOS {detail?.source ?? ""}
            </Text>
            {detail && (
              <>
                <Text style={styles.sheetBody}>
                  {triggerLabel[detail.trigger] ?? "?"} • hop {detail.hop ?? "?"} • pin{" "}
                  {detail.battery != null ? `${detail.battery}/15` : "?"} • GPS cấp{" "}
                  {detail.gps_fix ?? 0}
                </Text>
                <Text style={styles.sheetDim}>
                  Cập nhật {detail.age_s}s trước • {detail.frames} khung nhận được
                </Text>
              </>
            )}
            <Button onPress={() => {
              if (detail) setSelected(detail.source);
              setDetail(null);
              router.push("/compass");
            }}>
              Chỉ đường bằng la bàn
            </Button>
          </Column>
        </BottomSheet>
      </Host>

      {selected && !detail && (
        <Text style={styles.selectedNote}>Đang theo SOS {selected} — xem tab La bàn</Text>
      )}
    </View>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <View style={styles.legendItem}>
      <View style={[styles.legendDot, { backgroundColor: color }]} />
      <Text style={styles.legendText}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: palette.bg },
  pin: {
    width: 26,
    height: 26,
    borderRadius: 13,
    borderWidth: 2,
    borderColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
  },
  pinText: { color: "#fff", fontWeight: "800", fontSize: 13 },
  legend: {
    position: "absolute",
    top: spacing.s,
    left: spacing.s,
    backgroundColor: palette.surface + "E6",
    borderRadius: radius.m,
    padding: spacing.s,
    flexDirection: "row",
    gap: spacing.m,
  },
  legendItem: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  legendDot: { width: 10, height: 10, borderRadius: 5 },
  legendText: { color: palette.text, fontSize: 12 },
  sheet: { padding: spacing.l, gap: spacing.s },
  sheetTitle: { ...type.title, color: palette.text },
  sheetBody: { ...type.body, color: palette.text },
  sheetDim: { ...type.small, color: palette.textDim },
  selectedNote: {
    position: "absolute",
    bottom: spacing.m,
    alignSelf: "center",
    backgroundColor: palette.surface + "E6",
    color: palette.textDim,
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.m,
    borderRadius: radius.m,
    fontSize: 12,
  },
});
