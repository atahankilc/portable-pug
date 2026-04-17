import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from "react-native";
import { useAuth } from "../../src/context/AuthContext";
import { useRouter } from "expo-router";
import { getDeploymentMode } from "../../src/config/environment";

export default function HomeScreen() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.replace("/(auth)/login");
  }

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.welcome}>Welcome back!</Text>
      <Text style={styles.name}>{user?.full_name || user?.email}</Text>
      <View style={styles.card}>
        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>{user?.email}</Text>
        <Text style={styles.label}>Mode</Text>
        <Text style={styles.value}>{getDeploymentMode()}</Text>
      </View>
      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Sign Out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: "#F9FAFB" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  welcome: { fontSize: 16, color: "#6B7280", marginTop: 24 },
  name: { fontSize: 28, fontWeight: "700", color: "#111827", marginBottom: 24 },
  card: {
    backgroundColor: "#fff", borderRadius: 12, padding: 20,
    borderWidth: 1, borderColor: "#E5E7EB", marginBottom: 24,
  },
  label: { fontSize: 12, color: "#6B7280", marginTop: 12, marginBottom: 2 },
  value: { fontSize: 16, color: "#111827", fontWeight: "500" },
  logoutButton: {
    borderWidth: 1, borderColor: "#EF4444", borderRadius: 8,
    padding: 14, alignItems: "center",
  },
  logoutText: { color: "#EF4444", fontSize: 16, fontWeight: "600" },
});
