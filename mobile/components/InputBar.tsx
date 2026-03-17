import React, { useRef, useState } from "react";
import {
  Platform,
  Pressable,
  StyleSheet,
  TextInput,
  View,
} from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
} from "react-native-reanimated";

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function InputBar({ onSend, disabled }: Props) {
  const [text, setText] = useState("");
  const scale = useSharedValue(1);
  const inputRef = useRef<TextInput>(null);

  const canSend = text.trim().length > 0 && !disabled;

  const handleSend = () => {
    if (!canSend) return;
    onSend(text);
    setText("");
    // Keep keyboard open after sending — standard chat behavior
    inputRef.current?.focus();
  };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <View style={styles.container}>
      <View style={styles.inputWrapper}>
        <TextInput
          ref={inputRef}
          style={styles.input}
          value={text}
          onChangeText={setText}
          placeholder="Escribe tu mensaje..."
          placeholderTextColor="#9CA3AF"
          multiline
          maxLength={2000}
          editable={!disabled}
          // Keep keyboard open after submit
          blurOnSubmit={false}
          // iOS: sentence capitalization is natural for chat
          autoCapitalize="sentences"
          autoCorrect
          // iOS: light keyboard appearance
          keyboardAppearance="light"
          // iOS: adds some padding for text
          textAlignVertical="center"
        />
        <AnimatedPressable
          onPress={handleSend}
          onPressIn={() => {
            scale.value = withSpring(0.85);
          }}
          onPressOut={() => {
            scale.value = withSpring(1);
          }}
          disabled={!canSend}
          style={[
            styles.sendButton,
            canSend ? styles.sendButtonActive : styles.sendButtonDisabled,
            animatedStyle,
          ]}
          accessibilityRole="button"
          accessibilityLabel="Enviar mensaje"
        >
          <View style={styles.sendIconContainer}>
            <View style={[styles.sendArrowUp, canSend && styles.sendArrowUpActive]} />
            <View style={[styles.sendArrowLine, canSend && styles.sendArrowLineActive]} />
          </View>
        </AnimatedPressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    paddingBottom: Platform.OS === "ios" ? 4 : 8,
    backgroundColor: "#FFFFFF",
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: "#E5E7EB",
  },
  inputWrapper: {
    flexDirection: "row",
    alignItems: "flex-end",
    backgroundColor: "#F9FAFB",
    borderRadius: 24,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    paddingLeft: 16,
    paddingRight: 4,
    paddingVertical: 4,
  },
  input: {
    flex: 1,
    fontSize: 15,
    lineHeight: 20,
    maxHeight: 100,
    paddingVertical: 8,
    color: "#1F2937",
  },
  sendButton: {
    width: 38,
    height: 38,
    borderRadius: 19,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 1,
  },
  sendButtonActive: {
    backgroundColor: "#2563EB",
  },
  sendButtonDisabled: {
    backgroundColor: "#E5E7EB",
  },
  sendIconContainer: {
    alignItems: "center",
    justifyContent: "center",
    width: 16,
    height: 16,
  },
  sendArrowUp: {
    width: 0,
    height: 0,
    borderLeftWidth: 5,
    borderRightWidth: 5,
    borderBottomWidth: 7,
    borderLeftColor: "transparent",
    borderRightColor: "transparent",
    borderBottomColor: "#9CA3AF",
    marginBottom: 1,
  },
  sendArrowUpActive: {
    borderBottomColor: "#FFFFFF",
  },
  sendArrowLine: {
    width: 2,
    height: 6,
    backgroundColor: "#9CA3AF",
    borderRadius: 1,
  },
  sendArrowLineActive: {
    backgroundColor: "#FFFFFF",
  },
});
