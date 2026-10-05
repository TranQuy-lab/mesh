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
};

export default function RootLayout() {
  return (
    <ThemeProvider value={navTheme as never}>
      <StatusBar style="light" />
      <SosProvider />
    </ThemeProvider>
  );
}
