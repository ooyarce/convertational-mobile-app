import React, { createContext, useContext, useEffect, useReducer } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { STORAGE_KEY } from "../constants/config";
import {
  ConversationAction,
  ConversationState,
  Message,
  Role,
} from "../types/conversation";

const WELCOME_MESSAGE: Message = {
  id: "welcome",
  role: Role.ASSISTANT,
  content:
    "¡Hola! Soy PropAssist AI, tu asistente inmobiliario. ¿En qué puedo ayudarte hoy? Puedo buscar departamentos, casas, oficinas o terrenos según tus preferencias.",
  timestamp: Date.now(),
};

const initialState: ConversationState = {
  messages: [WELCOME_MESSAGE],
  isLoading: false,
  error: null,
};

function conversationReducer(
  state: ConversationState,
  action: ConversationAction
): ConversationState {
  switch (action.type) {
    case "ADD_MESSAGE":
      return { ...state, messages: [...state.messages, action.message], error: null };
    case "SET_LOADING":
      return { ...state, isLoading: action.isLoading };
    case "SET_ERROR":
      return { ...state, error: action.error, isLoading: false };
    case "LOAD":
      return { ...state, messages: action.messages.length > 0 ? action.messages : [WELCOME_MESSAGE] };
    case "CLEAR":
      return { ...initialState, messages: [{ ...WELCOME_MESSAGE, timestamp: Date.now() }] };
    default:
      return state;
  }
}

interface ConversationContextValue {
  state: ConversationState;
  dispatch: React.Dispatch<ConversationAction>;
}

const ConversationContext = createContext<ConversationContextValue | null>(null);

export function ConversationProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(conversationReducer, initialState);

  // Load persisted conversation on mount
  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((data) => {
      if (data) {
        try {
          const messages = JSON.parse(data) as Message[];
          dispatch({ type: "LOAD", messages });
        } catch {
          // Corrupted data, start fresh
        }
      }
    });
  }, []);

  // Persist on every message change
  useEffect(() => {
    AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(state.messages));
  }, [state.messages]);

  return (
    <ConversationContext.Provider value={{ state, dispatch }}>
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversationContext() {
  const ctx = useContext(ConversationContext);
  if (!ctx) {
    throw new Error("useConversationContext must be used within ConversationProvider");
  }
  return ctx;
}
