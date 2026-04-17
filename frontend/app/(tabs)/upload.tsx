import { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, Image, Platform } from "react-native";
import * as ImagePicker from "expo-image-picker";
import client from "../../src/api/client";

export default function UploadScreen() {
  const [image, setImage] = useState<ImagePicker.ImagePickerAsset | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ task_id: string; status: string; result?: any } | null>(null);

  async function pickImage() {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      Alert.alert("Permission required", "Please allow access to your photo library.");
      return;
    }
    const picked = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 0.8,
    });
    if (!picked.canceled && picked.assets.length > 0) {
      setImage(picked.assets[0]);
      setResult(null);
    }
  }

  async function upload() {
    if (!image) return;
    setLoading(true);
    try {
      const formData = new FormData();
      if (Platform.OS === "web") {
        const response = await fetch(image.uri);
        const blob = await response.blob();
        formData.append("image", blob, "upload.jpg");
      } else {
        formData.append("image", {
          uri: image.uri,
          name: "upload.jpg",
          type: "image/jpeg",
        } as any);
      }
      const res = await client.post("/ml/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch {
      Alert.alert("Upload failed", "Could not upload image.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Upload Image</Text>
      <TouchableOpacity style={styles.picker} onPress={pickImage}>
        {image ? (
          <Image source={{ uri: image.uri }} style={styles.preview} />
        ) : (
          <Text style={styles.pickerText}>Tap to select an image</Text>
        )}
      </TouchableOpacity>
      {image && (
        <TouchableOpacity style={styles.button} onPress={upload} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Analyze Image</Text>}
        </TouchableOpacity>
      )}
      {result && (
        <View style={styles.result}>
          <Text style={styles.resultLabel}>Result</Text>
          <Text style={styles.resultStatus}>Status: {result.status}</Text>
          {result.result && (
            <>
              <Text style={styles.resultValue}>Label: {result.result.label}</Text>
              <Text style={styles.resultValue}>Confidence: {(result.result.confidence * 100).toFixed(1)}%</Text>
            </>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: "#F9FAFB" },
  title: { fontSize: 24, fontWeight: "700", color: "#111827", marginBottom: 24 },
  picker: {
    height: 200, borderRadius: 12, borderWidth: 2, borderStyle: "dashed",
    borderColor: "#4F46E5", backgroundColor: "#EEF2FF", justifyContent: "center",
    alignItems: "center", marginBottom: 16, overflow: "hidden",
  },
  pickerText: { color: "#4F46E5", fontSize: 16 },
  preview: { width: "100%", height: "100%", resizeMode: "cover" },
  button: {
    backgroundColor: "#4F46E5", borderRadius: 8, padding: 16,
    alignItems: "center", marginBottom: 16,
  },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  result: {
    backgroundColor: "#fff", borderRadius: 12, padding: 20,
    borderWidth: 1, borderColor: "#E5E7EB",
  },
  resultLabel: { fontSize: 16, fontWeight: "700", color: "#111827", marginBottom: 8 },
  resultStatus: { fontSize: 14, color: "#6B7280", marginBottom: 4 },
  resultValue: { fontSize: 18, fontWeight: "600", color: "#4F46E5", marginBottom: 4 },
});
