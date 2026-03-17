# PropAssist AI

Asistente inmobiliario inteligente con IA conversacional y datos reales de propiedades.

- **Backend**: FastAPI + Gemini 2.5 Flash con function calling
- **Frontend**: React Native + Expo SDK 54 (TypeScript)

---

## Requisitos previos

| Herramienta | Versión | Verificar |
|-------------|---------|-----------|
| **Python** | 3.11+ | `python --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Docker** (opcional) | 20+ | `docker --version` |
| **Expo Go** (celular) | Última | App Store / Play Store |

---

## 1. Levantar el Backend

### PowerShell (Windows)

```powershell
cd backend

# Crear entorno virtual e instalar dependencias
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Iniciar servidor (0.0.0.0 permite acceso desde el celular)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Git Bash / macOS / Linux

```bash
cd backend

python -m venv venv
source venv/bin/activate          # macOS/Linux
# source venv/Scripts/activate    # Windows Git Bash
pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker (alternativa — sin instalar Python)

```bash
cd backend
docker compose up --build
```

> **Nota sobre `.env`**: El archivo `.env` con las API keys reales ya está configurado. Si necesitas recrearlo, copia `.env.example` y rellena los valores.

### Verificar que funciona

Abrir en el navegador o ejecutar:

```
http://localhost:8000/health
→ {"status":"ok"}
```

---

## 2. Levantar el Frontend

En **otra terminal**:

```powershell
cd mobile

# Instalar dependencias (solo la primera vez)
npm install --legacy-peer-deps

# Iniciar servidor de desarrollo
npx expo start
```

Esto muestra un QR code y un menú interactivo.

---

## 3. Dónde verlo

### PC — Navegador web

1. Con Expo corriendo, presiona **`w`** en la terminal
2. Se abre en **http://localhost:8081**
3. Funciona inmediatamente (el backend está en `localhost:8000`)

### iPhone — Expo Go

1. Instala **Expo Go** desde la App Store
2. Conecta tu iPhone a la **misma red WiFi** que tu PC
3. Escanea el **QR code** de la terminal con la cámara del iPhone
4. La app se abre en Expo Go y se conecta al backend automáticamente

### Android — Expo Go

1. Instala **Expo Go** desde Play Store
2. Misma red WiFi que tu PC
3. Presiona **`a`** en la terminal de Expo, o escanea el QR desde la app Expo Go

> **Importante**: El backend DEBE estar levantado con `--host 0.0.0.0` (no solo `localhost`) para que el celular pueda conectarse. La app detecta la IP de tu PC automáticamente.

---

## Resumen rápido

```
Terminal 1 (Backend):
  cd backend
  .\venv\Scripts\Activate.ps1
  uvicorn app.main:app --host 0.0.0.0 --port 8000

Terminal 2 (Frontend):
  cd mobile
  npx expo start
  → Presiona 'w' para web, o escanea QR para celular
```

| Qué | URL / Acceso |
|-----|-------------|
| Backend API | http://localhost:8000 |
| Health check | http://localhost:8000/health |
| Frontend web | http://localhost:8081 (presionar `w`) |
| Frontend celular | Escanear QR con Expo Go |

---

## Estructura del proyecto

```
/
├── backend/                  # FastAPI + Gemini + Function Calling
│   ├── app/
│   │   ├── api/              # POST /chat endpoint
│   │   ├── core/             # Agent, prompts, tools (function calling)
│   │   ├── schemas/          # Pydantic models
│   │   └── services/         # Cliente HTTP → API propiedades
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env                  # API keys (no versionado)
│   └── requirements.txt
│
├── mobile/                   # React Native + Expo SDK 54
│   ├── app/                  # Screens (Expo Router)
│   ├── components/           # MessageBubble, InputBar, Header, etc.
│   ├── context/              # ConversationContext (useReducer)
│   ├── hooks/                # useConversation
│   ├── services/             # POST /chat al backend
│   ├── types/                # TypeScript interfaces
│   └── constants/            # Config (URLs, timeouts)
│
├── PLAN.md                   # Plan de implementación detallado
└── README.md                 # Este archivo
```

---

## Decisiones técnicas

### LLM: Gemini 2.5 Flash (Google)

Elegí Gemini por tres razones principales:

1. **Function calling nativo**: Gemini soporta tool use de forma integrada en su SDK (`google-genai`), lo que permite que el modelo decida cuándo consultar la API de propiedades sin necesidad de parsear JSON manualmente ni de prompt hacks. Esto simplifica enormemente el flujo del agente.
2. **Tier gratuito generoso**: A diferencia de GPT-4o-mini que tiene un free trial limitado, Gemini ofrece un tier gratuito suficiente para desarrollo y demostración sin costo.
3. **Baja latencia**: Flash está optimizado para velocidad, lo que se traduce en respuestas más rápidas en el chat — crítico para una buena UX conversacional.

**Trade-off**: Groq (Llama 3.1) tiene latencia aún menor, pero su soporte de function calling es menos maduro y requiere parsing manual de las llamadas a herramientas. Claude Haiku ofrece excelente calidad pero el tier gratuito es más restrictivo.

### Backend: FastAPI + httpx + Pydantic

- **FastAPI**: Framework async nativo de Python. Validación automática de request/response con Pydantic, documentación OpenAPI generada automáticamente, y soporte nativo para `async/await` — ideal para un backend que hace múltiples llamadas HTTP concurrentes (API de propiedades + LLM).
- **httpx**: Cliente HTTP async compatible con el event loop de FastAPI. API idéntica a `requests` pero con soporte de `async/await`. Elegido sobre `aiohttp` por su API más limpia y mejor integración con el ecosistema Python moderno.
- **Pydantic**: Validación de datos en request/response con tipos estrictos. Integración nativa con FastAPI para serialización/deserialización automática.

### Frontend: Expo SDK 54 + Expo Router + Context API

- **Expo SDK 54**: La última versión estable del SDK. Permite desarrollo multiplataforma (iOS, Android, Web) con un solo codebase y sin necesidad de configurar Xcode/Android Studio para desarrollo.
- **Expo Router**: File-based routing inspirado en Next.js. Para una app de una sola pantalla (chat) es suficiente, y deja la puerta abierta a agregar más pantallas sin refactor.
- **Context + useReducer**: Para el estado del chat (mensajes, loading, error), un reducer es suficiente y predecible. Zustand o Redux agregarían una dependencia sin beneficio real — el estado es local a la conversación y no requiere middleware ni persistencia compleja.
- **StyleSheet nativo**: Sin NativeWind ni Tailwind. Para una UI de chat con pocos componentes, StyleSheet ofrece rendimiento óptimo (estilos compilados a nativos) sin el overhead de configuración de NativeWind. Los estilos son colocados junto a cada componente para mantener cohesión.

---

## Decisiones de UX

### Diseño general

La interfaz sigue el patrón de **app de mensajería** (WhatsApp, iMessage) por familiaridad. El usuario ya sabe cómo funciona un chat — no necesita aprender una interfaz nueva.

### Decisiones específicas

| Decisión | Por qué |
|----------|---------|
| **Burbujas diferenciadas** (azul usuario, gris IA) | Distinción visual inmediata de quién dice qué. Los colores siguen convenciones establecidas de apps de mensajería. |
| **Typing indicator animado** (tres puntos pulsantes) | Feedback visual mientras la IA procesa. Sin esto, el usuario no sabe si la app se colgó o está trabajando. Elegido sobre spinner porque se siente más conversacional. |
| **Suggestion chips al inicio** | Reducen la fricción del "¿qué le pregunto?". Muestran búsquedas comunes para que el usuario pueda empezar con un tap. Desaparecen una vez iniciada la conversación para no distraer. |
| **Error banner con retry** | Los errores de red/API son inevitables. En vez de un alert modal que interrumpe, un banner inline muestra el error y ofrece reintentar con un tap — sin perder el contexto de la conversación. |
| **Persistencia con AsyncStorage** | La conversación se guarda automáticamente. Si el usuario cierra la app y vuelve, encuentra su conversación donde la dejó. |
| **Haptic feedback** | Vibración sutil al enviar mensaje y al recibir respuesta. Refuerza la sensación de interactividad en dispositivos móviles. |
| **Auto-scroll** | Al recibir un mensaje nuevo, el chat hace scroll automático al final. Comportamiento esperado en cualquier app de mensajería. |
| **Max width 600px en web** | En pantallas grandes (desktop), el chat se centra con ancho máximo para mantener legibilidad. Líneas de texto demasiado largas son difíciles de leer. |

---

## ¿Qué mejorarías con 1 semana más?

### Respuestas en streaming (SSE)
Implementar Server-Sent Events para que la respuesta de la IA aparezca palabra por palabra en tiempo real, en vez de esperar a que se genere completa. Esto reduce drásticamente la percepción de latencia — el usuario empieza a leer antes de que termine la generación.

### Tarjetas de propiedades enriquecidas
En vez de mostrar las propiedades solo como texto, renderizar **tarjetas con imagen, precio, ubicación y características clave** directamente en el chat. Esto haría la experiencia mucho más visual y permitiría al usuario evaluar propiedades de un vistazo.

### Mapa interactivo
Integrar un mapa (Google Maps o Mapbox) que muestre la ubicación de las propiedades encontradas. El usuario podría ver dónde están las propiedades y hacer tap para ver detalles. Requiere coordenadas de la API.

### Historial de conversaciones
Permitir múltiples conversaciones guardadas con un sidebar o lista. Actualmente se persiste una sola conversación. Con historial, el usuario podría volver a búsquedas anteriores sin perder contexto.

### Búsqueda por voz
Integrar reconocimiento de voz (Expo Speech/Whisper) para que el usuario pueda dictar su búsqueda en vez de escribir. Especialmente útil en mobile donde escribir es más lento.

### Tests E2E
Agregar tests end-to-end con Detox (mobile) y Pytest + httpx para el backend. Actualmente hay tests unitarios básicos — falta cobertura de flujos completos como "usuario busca propiedad → recibe resultados → pide detalles".

### Caché inteligente
Cachear respuestas de la API de propiedades para búsquedas frecuentes (ej: "departamentos en Las Condes"). Reduciría latencia y consumo de API. Implementable con Redis o incluso un TTL cache en memoria.

### Dark mode
Soporte de tema oscuro respetando las preferencias del sistema operativo. La infraestructura de StyleSheet ya lo soporta con `useColorScheme()`.
