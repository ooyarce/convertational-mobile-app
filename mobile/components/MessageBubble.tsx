import React from "react";
import { Linking, Platform, StyleSheet, Text, View } from "react-native";
import { Message, Role } from "../types/conversation";

interface Props {
  message: Message;
}

/** Splits text into segments: plain, bold (**text**), and URLs. */
const SEGMENT_REGEX = /(\*\*(.+?)\*\*)|(https?:\/\/[^\s)]+)/g;

type Segment = { text: string; type: "plain" | "bold" | "url" };

function parseSegments(text: string): Segment[] {
  const segments: Segment[] = [];
  let lastIndex = 0;

  for (const match of text.matchAll(SEGMENT_REGEX)) {
    const start = match.index!;
    if (start > lastIndex) {
      segments.push({ text: text.slice(lastIndex, start), type: "plain" });
    }
    if (match[1]) {
      // **bold** — match[2] is the inner text without asterisks
      segments.push({ text: match[2], type: "bold" });
    } else {
      segments.push({ text: match[0], type: "url" });
    }
    lastIndex = start + match[0].length;
  }
  if (lastIndex < text.length) {
    segments.push({ text: text.slice(lastIndex), type: "plain" });
  }

  return segments.length > 0 ? segments : [{ text, type: "plain" }];
}

function AssistantAvatar() {
  return (
    <View style={styles.avatar}>
      <View style={styles.aiIcon}>
        <View style={styles.aiDiamond} />
        <View style={styles.aiDot} />
      </View>
    </View>
  );
}

/** Renders text with bold formatting and tappable URLs. */
function FormattedText({
  text,
  isUser,
}: {
  text: string;
  isUser: boolean;
}) {
  const segments = parseSegments(text);

  return (
    <Text style={[styles.text, isUser ? styles.textUser : styles.textAssistant]}>
      {segments.map((seg, i) => {
        if (seg.type === "bold") {
          return (
            <Text key={i} style={styles.bold}>
              {seg.text}
            </Text>
          );
        }
        if (seg.type === "url") {
          return (
            <Text
              key={i}
              style={isUser ? styles.linkUser : styles.linkAssistant}
              onPress={() => Linking.openURL(seg.text)}
            >
              {seg.text}
            </Text>
          );
        }
        return <Text key={i}>{seg.text}</Text>;
      })}
    </Text>
  );
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === Role.USER;

  return (
    <View style={[styles.row, isUser && styles.rowUser]}>
      {!isUser && <AssistantAvatar />}
      <View
        style={[
          styles.bubble,
          isUser ? styles.bubbleUser : styles.bubbleAssistant,
        ]}
      >
        <FormattedText text={message.content} isUser={isUser} />
        <Text style={[styles.time, isUser ? styles.timeUser : styles.timeAssistant]}>
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "flex-start",
    marginBottom: 4,
    paddingHorizontal: 12,
  },
  rowUser: {
    justifyContent: "flex-end",
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
    maxWidth: "75%",
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 18,
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.08,
        shadowRadius: 4,
      },
      android: {
        elevation: 1,
      },
      web: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.08,
        shadowRadius: 4,
      },
    }),
  },
  bubbleUser: {
    backgroundColor: "#2563EB",
    borderBottomRightRadius: 4,
    marginLeft: 48,
  },
  bubbleAssistant: {
    backgroundColor: "#F3F4F6",
    borderBottomLeftRadius: 4,
    marginRight: 48,
  },
  text: {
    fontSize: 15,
    lineHeight: 22,
  },
  textUser: {
    color: "#FFFFFF",
  },
  textAssistant: {
    color: "#1F2937",
  },
  bold: {
    fontWeight: "700",
  },
  linkUser: {
    color: "#BFDBFE",
    textDecorationLine: "underline",
  },
  linkAssistant: {
    color: "#2563EB",
    textDecorationLine: "underline",
  },
  time: {
    fontSize: 10,
    marginTop: 4,
    alignSelf: "flex-end",
  },
  timeUser: {
    color: "rgba(255,255,255,0.6)",
  },
  timeAssistant: {
    color: "#9CA3AF",
  },
});
