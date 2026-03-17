import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

interface Props {
  message: string;
  onDismiss: () => void;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onDismiss, onRetry }: Props) {
  return (
    <View style={styles.container}>
      <View style={styles.iconContainer}>
        <Text style={styles.icon}>!</Text>
      </View>
      <Text style={styles.text} numberOfLines={2}>
        {message}
      </Text>
      <View style={styles.actions}>
        {onRetry && (
          <Pressable
            onPress={onRetry}
            style={({ pressed }) => [styles.retryButton, pressed && styles.buttonPressed]}
          >
            <Text style={styles.retryText}>Reintentar</Text>
          </Pressable>
        )}
        <Pressable onPress={onDismiss} style={styles.dismissButton}>
          <Text style={styles.dismissText}>Cerrar</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FEF2F2",
    borderTopWidth: 1,
    borderTopColor: "#FECACA",
    paddingHorizontal: 12,
    paddingVertical: 10,
    gap: 10,
  },
  iconContainer: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: "#EF4444",
    justifyContent: "center",
    alignItems: "center",
  },
  icon: {
    color: "#FFFFFF",
    fontSize: 13,
    fontWeight: "800",
  },
  text: {
    flex: 1,
    fontSize: 13,
    color: "#991B1B",
    lineHeight: 18,
  },
  actions: {
    flexDirection: "row",
    gap: 6,
  },
  retryButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 14,
    backgroundColor: "#FEE2E2",
  },
  buttonPressed: {
    backgroundColor: "#FECACA",
  },
  retryText: {
    fontSize: 12,
    fontWeight: "700",
    color: "#DC2626",
  },
  dismissButton: {
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  dismissText: {
    fontSize: 12,
    fontWeight: "500",
    color: "#9CA3AF",
  },
});
