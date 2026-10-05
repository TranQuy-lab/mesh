/** Nguồn dữ liệu Console: poll /api/sos theo chu kỳ + lưu cấu hình. */
import AsyncStorage from "@react-native-async-storage/async-storage";

export type SosItem = {
  source: string;
  latitude: number | null;
  longitude: number | null;
  trigger: number;
  trigger_name: string;
  people: number | null;
  need: number | null;
  battery: number | null;
  gps_fix: number | null;
  hop: number | null;
  sequence: number;
  first_seen: number;
  last_seen: number;
  age_s: number;
  frames: number;
};

export const DEFAULT_SERVER = "http://127.0.0.1:8787";

const KEY = "server_url";

export async function loadServerUrl(): Promise<string> {
  try {
    return (await AsyncStorage.getItem(KEY)) || DEFAULT_SERVER;
  } catch {
    return DEFAULT_SERVER;
  }
}

export async function saveServerUrl(url: string): Promise<void> {
  await AsyncStorage.setItem(KEY, url.trim());
}

export async function fetchSos(serverUrl: string): Promise<SosItem[]> {
  const res = await fetch(`${serverUrl.replace(/\/$/, "")}/api/sos`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const body = (await res.json()) as { sos: SosItem[] };
  return body.sos ?? [];
}

/** Hình học: khoảng cách (m) và hướng (0° = bắc) giữa hai toạ độ. */
export function distanceMeters(a: [number, number], b: [number, number]): number {
  const R = 6371000;
  const rad = (x: number) => (x * Math.PI) / 180;
  const dp = rad(b[0] - a[0]);
  const dl = rad(b[1] - a[1]);
  const h =
    Math.sin(dp / 2) ** 2 +
    Math.cos(rad(a[0])) * Math.cos(rad(b[0])) * Math.sin(dl / 2) ** 2;
  return 2 * R * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

export function bearingDegrees(a: [number, number], b: [number, number]): number {
  const rad = (x: number) => (x * Math.PI) / 180;
  const deg = (x: number) => ((x * 180) / Math.PI + 360) % 360;
  const p1 = rad(a[0]);
  const p2 = rad(b[0]);
  const dl = rad(b[1] - a[1]);
  const y = Math.sin(dl) * Math.cos(p2);
  const x = Math.cos(p1) * Math.sin(p2) - Math.sin(p1) * Math.cos(p2) * Math.cos(dl);
  return deg(Math.atan2(y, x));
}

export const OCTANTS = ["B", "ĐB", "Đ", "ĐN", "N", "TN", "T", "TB"];
export function octant(bearing: number): string {
  return OCTANTS[Math.round(bearing / 45) % 8];
}
