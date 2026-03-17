import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { ConversationProvider } from "../context/ConversationContext";

export default function RootLayout() {
  return (
    <ConversationProvider>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false }} />
    </ConversationProvider>
  );
}
