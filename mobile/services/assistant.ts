import { BACKEND_URL, TIMEOUT_MS } from "../constants/config";
import { ConversationRequest, ConversationResponse } from "../types/conversation";

export async function sendMessage(
  request: ConversationRequest,
  signal?: AbortSignal
): Promise<ConversationResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

  // Link external abort signal to our controller
  if (signal) {
    signal.addEventListener("abort", () => controller.abort());
  }

  try {
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: controller.signal,
    });

    if (!response.ok) {
      // Try to get the detail message from the backend
      let detail = "";
      try {
        const body = await response.json();
        detail = body.detail || "";
      } catch {
        // ignore parse errors
      }

      if (response.status === 429 && detail) {
        throw new Error(detail);
      }

      const fallbacks: Record<number, string> = {
        429: "El servicio está saturado. Intenta de nuevo en unos segundos.",
        503: "El servicio de IA no está disponible temporalmente. Intenta en un momento.",
        500: "Ocurrió un error en el servidor. Intenta de nuevo.",
        502: "No se pudo conectar con el servicio de IA. Intenta de nuevo.",
      };
      throw new Error(detail || fallbacks[response.status] || `Error inesperado (${response.status}).`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === "AbortError") {
        throw new Error("La solicitud tardó demasiado. Intenta de nuevo.");
      }
      // Network errors (backend down, no internet, DNS failure)
      if (error.message === "Failed to fetch" || error.message.includes("Network")) {
        throw new Error("El servicio no está disponible en este momento. Intenta de nuevo más tarde.");
      }
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
