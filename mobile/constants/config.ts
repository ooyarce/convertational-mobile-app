import Constants from "expo-constants";
import { Platform } from "react-native";

// Resolve backend URL based on platform:
// - Web: localhost (same machine)
// - iOS device (Expo Go): use the dev machine IP from Expo's debuggerHost
// - Android emulator: 10.0.2.2 maps to host machine's localhost
const getBaseUrl = () => {
  if (Platform.OS === "web") return "http://localhost:8000";

  // Expo Go injects the dev machine IP via debuggerHost (e.g. "192.168.0.5:8081")
  const debuggerHost = Constants.expoConfig?.hostUri ?? Constants.experienceUrl;
  if (debuggerHost) {
    const ip = debuggerHost.split(":")[0];
    return `http://${ip}:8000`;
  }

  if (Platform.OS === "android") return "http://10.0.2.2:8000";
  return "http://localhost:8000";
};

export const BACKEND_URL = getBaseUrl();
export const TIMEOUT_MS = 60_000;
export const STORAGE_KEY = "propassist_conversation";
