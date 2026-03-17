import React, { useEffect, useRef } from "react";
import { FlatList, StyleSheet, View } from "react-native";
import { Message } from "../types/conversation";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

interface Props {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: Props) {
  const flatListRef = useRef<FlatList<Message>>(null);

  // Scroll to bottom whenever a new message arrives or loading changes
  useEffect(() => {
    if (messages.length === 0) return;
    const timer = setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 150);
    return () => clearTimeout(timer);
  }, [messages.length, isLoading]);

  return (
    <FlatList
      ref={flatListRef}
      data={messages}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <MessageBubble message={item} />}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
      ListFooterComponent={isLoading ? <TypingIndicator /> : null}
      ItemSeparatorComponent={() => <View style={styles.separator} />}
      keyboardShouldPersistTaps="handled"
    />
  );
}

const styles = StyleSheet.create({
  content: {
    paddingVertical: 16,
    flexGrow: 1,
  },
  separator: {
    height: 2,
  },
});
