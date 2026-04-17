import { Tabs } from "expo-router";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#4F46E5",
        tabBarInactiveTintColor: "#6B7280",
        headerStyle: { backgroundColor: "#4F46E5" },
        headerTintColor: "#fff",
      }}
    >
      <Tabs.Screen name="home" options={{ title: "Home" }} />
      <Tabs.Screen name="upload" options={{ title: "Upload" }} />
      <Tabs.Screen name="results" options={{ title: "Results" }} />
    </Tabs>
  );
}
