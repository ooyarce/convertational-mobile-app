export enum Role {
  USER = "user",
  ASSISTANT = "assistant",
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: number;
}

export interface ConversationRequest {
  message: string;
  history: { role: Role; content: string }[];
}

export interface ConversationResponse {
  role: Role;
  content: string;
}

export interface ConversationState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export type ConversationAction =
  | { type: "ADD_MESSAGE"; message: Message }
  | { type: "SET_LOADING"; isLoading: boolean }
  | { type: "SET_ERROR"; error: string | null }
  | { type: "LOAD"; messages: Message[] }
  | { type: "CLEAR" };
