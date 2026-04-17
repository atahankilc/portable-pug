import Constants from "expo-constants";
import { Platform } from "react-native";

export function isElectron(): boolean {
  if (Platform.OS !== "web") return false;
  if (typeof window === "undefined") return false;
  return !!(window as any).electronAPI?.isElectron;
}

export function getDeploymentMode(): string {
  if (isElectron()) {
    return (window as any).electronAPI?.deploymentMode ?? "local";
  }
  return Constants.expoConfig?.extra?.DEPLOYMENT_MODE ?? "local";
}

export function getApiBaseUrl(): string {
  if (isElectron()) {
    const mode = getDeploymentMode();
    if (mode === "cloud") {
      return Constants.expoConfig?.extra?.API_URL ?? "http://localhost:8000/api/";
    }
    return "http://localhost:8000/api/";
  }
  return Constants.expoConfig?.extra?.API_URL ?? "http://localhost:8000/api/";
}
