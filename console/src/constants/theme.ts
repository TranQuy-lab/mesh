/**
 * Design tokens — nguồn chân lý duy nhất cho giao diện RescueSOS Console
 * (expo-design-system: màu/chữ/khoảng cách/radius đặt tập trung, không hard-code).
 * Theme "khẩn cấp": nền tối, đỏ SOS, xanh an toàn — tương phản cao, dùng ngoài nắng.
 */
export const palette = {
  bg: "#0E1116",
  surface: "#171C24",
  surfaceAlt: "#1F2630",
  border: "#2A3340",
  text: "#EAF0F7",
  textDim: "#93A1B3",
  sos: "#E53935",
  sosPressed: "#B71C1C",
  water: "#AB47BC", // trigger chìm (H7)
  manual: "#FB8C00", // trigger tay
  safe: "#43A047",
  link: "#64B5F6",
} as const;

export const triggerColor: Record<number, string> = {
  1: palette.manual, // tay
  2: palette.sos, // ngã
  3: palette.water, // chìm
};

export const triggerLabel: Record<number, string> = {
  1: "Bấm tay",
  2: "Ngã (IMU)",
  3: "Chìm (H7)",
};

export const spacing = { xs: 4, s: 8, m: 16, l: 24, xl: 32 } as const;
export const radius = { s: 8, m: 14, l: 22 } as const;
export const type = {
  title: { fontSize: 22, fontWeight: "700" as const },
  heading: { fontSize: 17, fontWeight: "600" as const },
  body: { fontSize: 15, fontWeight: "400" as const },
  small: { fontSize: 13, fontWeight: "400" as const },
  big: { fontSize: 34, fontWeight: "800" as const },
};
