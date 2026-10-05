import { Tabs } from "expo-router";
import Ionicons from "@expo/vector-icons/Ionicons";

import { palette } from "@/constants/theme";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: palette.surface },
        headerTintColor: palette.text,
        sceneStyle: { backgroundColor: palette.bg },
        tabBarStyle: { backgroundColor: palette.surface, borderTopColor: palette.border },
        tabBarActiveTintColor: palette.sos,
        tabBarInactiveTintColor: palette.textDim,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Bản đồ",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="map-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="compass"
        options={{
          title: "La bàn",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="compass-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="sos"
        options={{
          title: "SOS",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="notifications-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: "Cấu hình",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="settings-outline" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
