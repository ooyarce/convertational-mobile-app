import { useCallback, useRef } from "react";
import * as Haptics from "expo-haptics";
import { useConversationContext } from "../context/ConversationContext";
import { sendMessage } from "../services/assistant";
import { Message, Role } from "../types/conversation";

function createMessage(role: Role, content: string): Message {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    role,
    content,
    timestamp: Date.now(),
  };
}

export function useConversation() {
  const { state, dispatch } = useConversationContext();
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || state.isLoading) return;

      // Haptic feedback on send
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

      // Add user message
      const userMsg = createMessage(Role.USER, trimmed);
      dispatch({ type: "ADD_MESSAGE", message: userMsg });
      dispatch({ type: "SET_LOADING", isLoading: true });

      // Build history for backend (exclude welcome message and current message)
      const history = state.messages
        .filter((m) => m.id !== "welcome")
        .map((m) => ({ role: m.role, content: m.content }));

      // Abort any in-flight request
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const response = await sendMessage(
          { message: trimmed, history },
          controller.signal
        );

        const assistantMsg = createMessage(Role.ASSISTANT, response.content);
        dispatch({ type: "ADD_MESSAGE", message: assistantMsg });
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } catch (error) {
        if (controller.signal.aborted) return; // Cancelled, ignore
        const errorMessage =
          error instanceof Error
            ? error.message
            : "Ocurrió un error inesperado.";
        dispatch({ type: "SET_ERROR", error: errorMessage });
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      } finally {
        dispatch({ type: "SET_LOADING", isLoading: false });
      }
    },
    [state.messages, state.isLoading, dispatch]
  );

  const clear = useCallback(() => {
    abortRef.current?.abort();
    dispatch({ type: "CLEAR" });
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  }, [dispatch]);

  const retry = useCallback(() => {
    dispatch({ type: "SET_ERROR", error: null });
    // Find the last user message and resend it
    const lastUserMsg = [...state.messages]
      .reverse()
      .find((m) => m.role === Role.USER);
    if (lastUserMsg) {
      // Remove the last user message so send() can re-add it
      dispatch({ type: "SET_LOADING", isLoading: false });
      send(lastUserMsg.content);
    }
  }, [state.messages, dispatch, send]);

  const dismissError = useCallback(() => {
    dispatch({ type: "SET_ERROR", error: null });
  }, [dispatch]);

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    send,
    clear,
    retry,
    dismissError,
  };
}
