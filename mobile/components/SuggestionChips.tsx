import React from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

const SUGGESTIONS = [
  "Departamentos en La Reina",
  "Casas en La Serena",
  "Arriendos en Concepción",
  "Propiedades hasta 5.000 UF",
];

interface Props {
  onSelect: (text: string) => void;
  visible: boolean;
}

export function SuggestionChips({ onSelect, visible }: Props) {
  if (!visible) return null;

  return (
    <View style={styles.wrapper}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
      >
        {SUGGESTIONS.map((suggestion) => (
          <Pressable
            key={suggestion}
            style={({ pressed }) => [
              styles.chip,
              pressed && styles.chipPressed,
            ]}
            onPress={() => onSelect(suggestion)}
          >
            <Text style={styles.chipText}>{suggestion}</Text>
          </Pressable>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: "#E5E7EB",
  },
  container: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 10,
    gap: 8,
  },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#EFF6FF",
    borderWidth: 1,
    borderColor: "#BFDBFE",
  },
  chipPressed: {
    backgroundColor: "#DBEAFE",
  },
  chipText: {
    fontSize: 13,
    color: "#2563EB",
    fontWeight: "500",
  },
});
