import React, { useEffect } from "react";
import { StyleSheet, View } from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withRepeat,
  withSequence,
  withTiming,
} from "react-native-reanimated";

function Dot({ delay }: { delay: number }) {
  const translateY = useSharedValue(0);

  useEffect(() => {
    translateY.value = withDelay(
      delay,
      withRepeat(
        withSequence(
          withTiming(-4, { duration: 300 }),
          withTiming(0, { duration: 300 })
        ),
        -1,
        false
      )
    );
  }, [delay, translateY]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
  }));

  return <Animated.View style={[styles.dot, animatedStyle]} />;
}

export function TypingIndicator() {
  return (
    <View style={styles.container}>
      <View style={styles.avatar}>
        <View style={styles.aiIcon}>
          <View style={styles.aiDiamond} />
          <View style={styles.aiDot} />
        </View>
      </View>
      <View style={styles.bubble}>
        <Dot delay={0} />
        <Dot delay={150} />
        <Dot delay={300} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "flex-end",
    paddingHorizontal: 12,
    marginBottom: 4,
  },
  avatar: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: "#2563EB",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 8,
    marginBottom: 2,
  },
  aiIcon: {
    alignItems: "center",
    justifyContent: "center",
  },
  aiDiamond: {
    width: 10,
    height: 10,
    backgroundColor: "#FFFFFF",
    transform: [{ rotate: "45deg" }],
  },
  aiDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: "#FFFFFF",
    marginTop: 2,
  },
  bubble: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#F3F4F6",
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    gap: 5,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#9CA3AF",
  },
});
