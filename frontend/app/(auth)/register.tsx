import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import client, { storeTokens } from "../../src/api/client";

export default function RegisterScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleRegister() {
    if (!email || !password || !fullName) {
      Alert.alert("Error", "Please fill in all fields.");
      return;
    }
    setLoading(true);
    try {
      const res = await client.post("/register/", { email, password, full_name: fullName });
      await storeTokens(res.data.access, res.data.refresh);
      router.replace("/(tabs)/home");
    } catch (err: any) {
      const msg = err?.response?.data?.email?.[0] ?? "Registration failed.";
      Alert.alert("Error", msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Account</Text>
      <TextInput style={styles.input} placeholder="Full Name" value={fullName} onChangeText={setFullName} />
      <TextInput
        style={styles.input} placeholder="Email"
        autoCapitalize="none" keyboardType="email-address"
        value={email} onChangeText={setEmail}
      />
      <TextInput
        style={styles.input} placeholder="Password (min 8 chars)"
        secureTextEntry value={password} onChangeText={setPassword}
      />
      <TouchableOpacity style={styles.button} onPress={handleRegister} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Register</Text>}
      </TouchableOpacity>
      <TouchableOpacity onPress={() => router.push("/(auth)/login")}>
        <Text style={styles.link}>Already have an account? Sign In</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24, backgroundColor: "#F9FAFB" },
  title: { fontSize: 28, fontWeight: "700", marginBottom: 32, color: "#111827", textAlign: "center" },
  input: {
    borderWidth: 1, borderColor: "#E5E7EB", borderRadius: 8,
    padding: 14, marginBottom: 16, backgroundColor: "#fff", fontSize: 16,
  },
  button: {
    backgroundColor: "#4F46E5", borderRadius: 8, padding: 16,
    alignItems: "center", marginBottom: 16,
  },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  link: { color: "#4F46E5", textAlign: "center", fontSize: 14 },
});
