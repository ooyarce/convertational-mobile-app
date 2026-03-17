import React, { useCallback, useState } from "react";
import { Alert, Modal, Platform, Pressable, StyleSheet, Text, View } from "react-native";

interface Props {
  onNewConversation: () => void;
  hasMessages?: boolean;
}

export function Header({ onNewConversation, hasMessages }: Props) {
  const [showModal, setShowModal] = useState(false);

  const handleNewPress = useCallback(() => {
    if (!hasMessages) {
      onNewConversation();
      return;
    }
    if (Platform.OS === "web") {
      setShowModal(true);
    } else {
      Alert.alert(
        "Nueva conversación",
        "Se perderá la conversación actual. ¿Deseas continuar?",
        [
          { text: "Cancelar", style: "cancel" },
          { text: "Sí, nueva", style: "destructive", onPress: onNewConversation },
        ]
      );
    }
  }, [hasMessages, onNewConversation]);

  return (
    <View style={styles.container}>
      <View style={styles.left}>
        <View style={styles.avatarContainer}>
          <View style={styles.avatar}>
            <View style={styles.aiIcon}>
              <View style={styles.aiDiamond} />
              <View style={styles.aiDot} />
            </View>
          </View>
          <View style={styles.onlineDot} />
        </View>
        <View>
          <Text style={styles.title}>PropAssist AI</Text>
          <Text style={styles.subtitle}>Asistente inmobiliario</Text>
        </View>
      </View>
      <Pressable
        onPress={handleNewPress}
        disabled={!hasMessages}
        style={({ pressed }) => [
          styles.newButton,
          hasMessages ? (pressed && styles.newButtonPressed) : styles.newButtonDisabled,
        ]}
      >
        <Text style={[styles.newButtonIcon, !hasMessages && styles.newButtonTextDisabled]}>+</Text>
        <Text style={[styles.newButtonText, !hasMessages && styles.newButtonTextDisabled]}>Nuevo chat</Text>
      </Pressable>

      {/* Web confirmation modal (Alert doesn't work on web) */}
      <Modal visible={showModal} transparent animationType="fade">
        <Pressable style={styles.modalOverlay} onPress={() => setShowModal(false)}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>Nueva conversación</Text>
            <Text style={styles.modalMessage}>
              Se perderá la conversación actual. ¿Deseas continuar?
            </Text>
            <View style={styles.modalButtons}>
              <Pressable
                style={[styles.modalBtn, styles.modalBtnCancel]}
                onPress={() => setShowModal(false)}
              >
                <Text style={styles.modalBtnCancelText}>Cancelar</Text>
              </Pressable>
              <Pressable
                style={[styles.modalBtn, styles.modalBtnConfirm]}
                onPress={() => { setShowModal(false); onNewConversation(); }}
              >
                <Text style={styles.modalBtnConfirmText}>Sí, nueva</Text>
              </Pressable>
            </View>
          </View>
        </Pressable>
      </Modal>
    </View>
  );
}

const shadow = Platform.select({
  ios: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
  },
  android: { elevation: 2 },
  web: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
  },
});

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#FFFFFF",
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "#E5E7EB",
    ...shadow,
  },
  left: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  avatarContainer: {
    position: "relative",
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#2563EB",
    justifyContent: "center",
    alignItems: "center",
  },
  aiIcon: {
    alignItems: "center",
    justifyContent: "center",
  },
  aiDiamond: {
    width: 14,
    height: 14,
    backgroundColor: "#FFFFFF",
    transform: [{ rotate: "45deg" }],
  },
  aiDot: {
    width: 5,
    height: 5,
    borderRadius: 2.5,
    backgroundColor: "#FFFFFF",
    marginTop: 3,
  },
  onlineDot: {
    position: "absolute",
    bottom: 0,
    right: 0,
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: "#22C55E",
    borderWidth: 2,
    borderColor: "#FFFFFF",
  },
  title: {
    fontSize: 17,
    fontWeight: "700",
    color: "#1F2937",
  },
  subtitle: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 1,
  },
  newButton: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#EFF6FF",
    gap: 4,
  },
  newButtonPressed: {
    backgroundColor: "#DBEAFE",
  },
  newButtonDisabled: {
    backgroundColor: "#F3F4F6",
    opacity: 0.5,
  },
  newButtonTextDisabled: {
    color: "#9CA3AF",
  },
  newButtonIcon: {
    fontSize: 16,
    fontWeight: "600",
    color: "#2563EB",
  },
  newButtonText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#2563EB",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.4)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalBox: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 24,
    width: 300,
    alignItems: "center",
  },
  modalTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#1F2937",
    marginBottom: 8,
  },
  modalMessage: {
    fontSize: 14,
    color: "#6B7280",
    textAlign: "center",
    lineHeight: 20,
    marginBottom: 20,
  },
  modalButtons: {
    flexDirection: "row",
    gap: 12,
  },
  modalBtn: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10,
  },
  modalBtnCancel: {
    backgroundColor: "#F3F4F6",
  },
  modalBtnCancelText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#6B7280",
  },
  modalBtnConfirm: {
    backgroundColor: "#EF4444",
  },
  modalBtnConfirmText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#FFFFFF",
  },
});
