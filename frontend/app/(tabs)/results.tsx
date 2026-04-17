import { useState, useEffect, useCallback } from "react";
import { View, Text, FlatList, StyleSheet, ActivityIndicator, TouchableOpacity, RefreshControl } from "react-native";
import client from "../../src/api/client";

interface MLJob {
  id: number;
  task_id: string;
  task_type: string;
  status: string;
  result: { label: string; confidence: number } | null;
  created_at: string;
}

export default function ResultsScreen() {
  const [jobs, setJobs] = useState<MLJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function fetchResults() {
    try {
      const res = await client.get("/ml/results/");
      setJobs(res.data);
    } catch {}
  }

  useEffect(() => {
    fetchResults().finally(() => setLoading(false));
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchResults();
    setRefreshing(false);
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={jobs}
        keyExtractor={(item) => item.task_id}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No results yet. Upload an image to get started.</Text>
          </View>
        }
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.row}>
              <Text style={styles.label}>{item.result?.label ?? "—"}</Text>
              <Text style={styles.confidence}>
                {item.result ? `${(item.result.confidence * 100).toFixed(1)}%` : ""}
              </Text>
            </View>
            <Text style={styles.meta}>{new Date(item.created_at).toLocaleString()}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F9FAFB", padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  empty: { padding: 48, alignItems: "center" },
  emptyText: { color: "#6B7280", fontSize: 15, textAlign: "center" },
  card: {
    backgroundColor: "#fff", borderRadius: 12, padding: 16,
    marginBottom: 12, borderWidth: 1, borderColor: "#E5E7EB",
  },
  row: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 4 },
  label: { fontSize: 18, fontWeight: "700", color: "#111827", textTransform: "capitalize" },
  confidence: { fontSize: 16, fontWeight: "600", color: "#4F46E5" },
  meta: { fontSize: 12, color: "#9CA3AF" },
});
