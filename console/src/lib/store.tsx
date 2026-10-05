/** Nguồn dữ liệu chia sẻ: poll /api/sos 5 s/lượt, cấu hình server, người + SOS được chọn. */
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Slot } from "expo-router";
import * as Location from "expo-location";

import { DEFAULT_SERVER, fetchSos, loadServerUrl, saveServerUrl, type SosItem } from "./api";

type OwnPosition = { lat: number; lon: number; accuracy: number | null } | null;

type Store = {
  serverUrl: string;
  setServerUrl: (url: string) => Promise<void>;
  sos: SosItem[];
  status: "idle" | "ok" | "error";
  error: string | null;
  lastRefresh: number | null;
  refresh: () => Promise<void>;
  selected: string | null;
  setSelected: (source: string | null) => void;
  own: OwnPosition;
  heading: number | null;
};

const StoreContext = createContext<Store | null>(null);

export function useSosStore(): Store {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error("useSosStore phải nằm trong <SosProvider>");
  return ctx;
}

export function SosProvider() {
  const [serverUrl, setUrl] = useState(DEFAULT_SERVER);
  const [sos, setSos] = useState<SosItem[]>([]);
  const [status, setStatus] = useState<Store["status"]>("idle");
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLast] = useState<number | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [own, setOwn] = useState<OwnPosition>(null);
  const [heading, setHeading] = useState<number | null>(null);
  const urlRef = useRef(serverUrl);
  urlRef.current = serverUrl;

  useEffect(() => {
    loadServerUrl().then(setUrl);
  }, []);

  const refresh = useCallback(async () => {
    try {
      const list = await fetchSos(urlRef.current);
      setSos(list);
      setStatus("ok");
      setError(null);
      setLast(Date.now());
    } catch (e) {
      setStatus("error");
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, [refresh]);

  // Vị trí + hướng la bàn của người cầm máy (đội cứu hộ)
  useEffect(() => {
    let sub: Location.LocationSubscription | null = null;
    let headSub: Location.LocationSubscription | null = null;
    (async () => {
      const { status: ps } = await Location.requestForegroundPermissionsAsync();
      if (ps !== "granted") return;
      const pos = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      setOwn({ lat: pos.coords.latitude, lon: pos.coords.longitude, accuracy: pos.coords.accuracy });
      sub = await Location.watchPositionAsync(
        { accuracy: Location.Accuracy.Balanced, timeInterval: 5000, distanceInterval: 5 },
        (p) => setOwn({ lat: p.coords.latitude, lon: p.coords.longitude, accuracy: p.coords.accuracy })
      );
      headSub = await Location.watchHeadingAsync((h) => {
        const t = h.trueHeading >= 0 ? h.trueHeading
          : h.magHeading >= 0 ? h.magHeading : null;
        if (t != null && !Number.isNaN(t)) setHeading(t);
      });
    })();
    return () => {
      sub?.remove();
      headSub?.remove();
    };
  }, []);

  const setServerUrl = useCallback(async (url: string) => {
    await saveServerUrl(url);
    setUrl(url.trim());
  }, []);

  const value = useMemo<Store>(
    () => ({
      serverUrl,
      setServerUrl,
      sos,
      status,
      error,
      lastRefresh,
      refresh,
      selected,
      setSelected,
      own,
      heading,
    }),
    [serverUrl, setServerUrl, sos, status, error, lastRefresh, refresh, selected, own, heading]
  );

  return (
    <StoreContext.Provider value={value}>
      <Slot />
    </StoreContext.Provider>
  );
}
