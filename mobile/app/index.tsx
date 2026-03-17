import React, { useEffect, useState } from "react";
import {
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Header } from "../components/Header";
import { MessageList } from "../components/MessageList";
import { InputBar } from "../components/InputBar";
import { SuggestionChips } from "../components/SuggestionChips";
import { ErrorBanner } from "../components/ErrorBanner";
import { useConversation } from "../hooks/useConversation";

export default function ChatScreen() {
  const { messages, isLoading, error, send, clear, retry, dismissError } =
    useConversation();
  const insets = useSafeAreaInsets();
  const [keyboardHeight, setKeyboardHeight] = useState(0);

  useEffect(() => {
    const showSub = Keyboard.addListener(
      Platform.OS === "ios" ? "keyboardWillShow" : "keyboardDidShow",
      (e) => setKeyboardHeight(e.endCoordinates.height)
    );
    const hideSub = Keyboard.addListener(
      Platform.OS === "ios" ? "keyboardWillHide" : "keyboardDidHide",
      () => setKeyboardHeight(0)
    );
    return () => {
      showSub.remove();
      hideSub.remove();
    };
  }, []);

  const showSuggestions = messages.length <= 1 && !isLoading;
  const isKeyboardOpen = keyboardHeight > 0;

  // When keyboard is closed, add bottom inset for home indicator.
  // When keyboard is open, the keyboard already covers the home indicator.
  const bottomPadding = isKeyboardOpen ? keyboardHeight : insets.bottom;

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <Header onNewConversation={clear} hasMessages={messages.length > 1} />

      <View style={styles.flex}>
        <MessageList messages={messages} isLoading={isLoading} />
      </View>

      {showSuggestions && !isKeyboardOpen && (
        <SuggestionChips onSelect={send} visible />
      )}

      {error && (
        <ErrorBanner
          message={error}
          onDismiss={dismissError}
          onRetry={retry}
        />
      )}

      <View style={{ paddingBottom: bottomPadding, backgroundColor: "#FFFFFF" }}>
        <InputBar onSend={send} disabled={isLoading} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    maxWidth: 600,
    width: "100%",
    alignSelf: "center",
  },
  flex: {
    flex: 1,
  },
});
