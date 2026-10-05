import { useEffect } from "react";
import { ThemeProvider } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";

import { palette } from "@/constants/theme";
import { SosProvider } from "@/lib/store";

SplashScreen.preventAutoHideAsync();

const navTheme = {
  dark: true,
  colors: {
    primary: palette.sos,
    background: palette.bg,
    card: palette.surface,
    text: palette.text,
    border: palette.border,
    notification: palette.sos,
  },
  // React Navigation 7 bắt buộc fonts — thiếu sẽ crash HeaderTitle ('bold' of undefined)
  fonts: {
    regular: { fontFamily: "System", fontWeight: "400" as const },
    medium: { fontFamily: "System", fontWeight: "500" as const },
    bold: { fontFamily: "System", fontWeight: "700" as const },
    heavy: { fontFamily: "System", fontWeight: "900" as const },
  },
};

export default function RootLayout() {
  useEffect(() => {
    SplashScreen.hideAsync().catch(() => {});
  }, []);
  return (
    <ThemeProvider value={navTheme as never}>
      <StatusBar style="light" />
      <SosProvider />
    </ThemeProvider>
  );
}
