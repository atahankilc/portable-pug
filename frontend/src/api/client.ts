import axios from "axios";
import { Platform } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getApiBaseUrl } from "../config/environment";

const TOKEN_KEY = "auth_access_token";
const REFRESH_KEY = "auth_refresh_token";

async function getToken(): Promise<string | null> {
  if (Platform.OS === "web") {
    return localStorage.getItem(TOKEN_KEY);
  }
  return AsyncStorage.getItem(TOKEN_KEY);
}

async function getRefreshToken(): Promise<string | null> {
  if (Platform.OS === "web") {
    return localStorage.getItem(REFRESH_KEY);
  }
  return AsyncStorage.getItem(REFRESH_KEY);
}

export async function storeTokens(access: string, refresh: string): Promise<void> {
  if (Platform.OS === "web") {
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  } else {
    await AsyncStorage.setItem(TOKEN_KEY, access);
    await AsyncStorage.setItem(REFRESH_KEY, refresh);
  }
}

export async function clearTokens(): Promise<void> {
  if (Platform.OS === "web") {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
  } else {
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(REFRESH_KEY);
  }
}

const client = axios.create({
  baseURL: getApiBaseUrl(),
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh = await getRefreshToken();
      if (refresh) {
        try {
          const res = await axios.post(`${getApiBaseUrl()}token/refresh/`, { refresh });
          const { access } = res.data;
          await storeTokens(access, refresh);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return client(originalRequest);
        } catch {
          await clearTokens();
        }
      }
    }
    return Promise.reject(error);
  }
);

export default client;
