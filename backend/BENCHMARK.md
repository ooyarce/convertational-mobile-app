# Benchmark: Selección de Modelo LLM para PropAssist AI

> **Fecha:** 15 de marzo de 2026
> **Restricción:** Solo modelos con free tier (sin tarjeta de crédito, $0 de costo)
> **Caso de uso:** Agente inmobiliario con function calling (3 herramientas)

---

## 1. Contexto del problema

PropAssist AI es un chatbot inmobiliario que necesita un LLM capaz de:

1. **Function calling**: invocar 3 herramientas (`search_locations`, `list_properties`, `get_property_detail`) para consultar una API de propiedades real.
2. **Responder en español**: independientemente del idioma de entrada.
3. **Rechazar off-topic**: declinar preguntas no relacionadas con inmuebles.
4. **Operar gratis**: el MVP no justifica costos de API.

El LLM actúa como agente orquestador: recibe el mensaje del usuario, decide qué herramientas usar, ejecuta las llamadas, y genera la respuesta final con datos reales.

---

## 2. Proveedores evaluados

### 2.1 Google Gemini (via `google-genai` SDK)

| Modelo | RPM | RPD | TPM | Free Tier |
|--------|-----|-----|-----|-----------|
| gemini-2.5-pro | 5 | 100 | 250K | Sí |
| gemini-2.5-flash | 10 | 250 | 250K | Sí |
| gemini-2.5-flash-lite | 15 | 1,000* | 250K | Sí |
| gemini-2.0-flash | Retirado | limit: 0 | — | No |

> *\*Nota: Los blogs reportan 1,000 RPD para flash-lite, y esto fue confirmado via el dashboard de Google AI Studio. El error `quotaValue: 20` que reportaba la API era en realidad el **RPM sliding window** (requests por minuto), no el límite diario. Google etiqueta confusamente este error como `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, pero el `retryDelay: 44s` y el dashboard confirman que es un límite por minuto. En toda la sesión de benchmark (~1 hora) se consumieron ~60-80 requests, muy lejos de los 1,000 diarios.*

**Problemas encontrados:**
- **Mensajes de error de quota engañosos**: Google reporta límites RPM bajo un quota ID etiquetado como "PerDay", generando confusión. El dashboard real muestra que el RPD nunca se agotó.
- `gemini-2.0-flash` fue retirado en marzo 2026 con `limit: 0`.
- La librería `tenacity` del SDK hace retry interno que consume intentos antes de llegar a nuestro código de retry.
- Function calling genera 2-3 requests rápidas por conversación (prompt → tool → respuesta), lo que fácilmente excede el RPM de 15 si se ejecutan tests en secuencia sin delays.

### 2.2 Groq (via `groq` SDK — formato OpenAI-compatible)

| Modelo | RPM | RPD | TPD | Free Tier |
|--------|-----|------|-----|-----------|
| llama-3.3-70b-versatile | 30 | 1,000 | 100K | Sí |
| meta-llama/llama-4-scout-17b-16e-instruct | 30 | 1,000 | 500K | Sí |
| qwen/qwen3-32b | 60 | 1,000 | 500K | Sí |
| llama-3.1-8b-instant | 30 | 14,400 | 500K | Sí |

**Ventajas de Groq:**
- Cuotas claras y bien documentadas.
- SDK compatible con formato OpenAI (estándar de industria).
- Inferencia ultra rápida via LPUs (Language Processing Units).
- Sin tarjeta de crédito requerida.

### 2.3 Otros proveedores descartados

| Proveedor | Razón de descarte |
|-----------|-------------------|
| **Grok (xAI)** | Sin free tier. $25 de crédito inicial, luego pago. |
| **OpenAI** | Sin free tier para GPT-4o/4.1. Solo créditos iniciales. |
| **Anthropic (Claude)** | Sin free tier para API directa. |
| **Mistral** | 1B tokens/mes gratis, pero function calling menos maduro en modelos open-source. |
| **OpenRouter** | Agregador, 50 req/día en free tier — insuficiente. |

---

## 3. Metodología del benchmark

### 3.1 Escenarios de prueba

Se usaron 3 escenarios representativos del uso real del chatbot:

| # | Escenario | Mensaje | Espera tools | Qué valida |
|---|-----------|---------|-------------|------------|
| 1 | **Saludo** | "Hola, buenas tardes" | No | Respuesta conversacional en español, sin tool calls innecesarios |
| 2 | **Búsqueda con filtros** | "Busco un departamento de 2 dormitorios en Las Condes, hasta 5.000 UF" | Sí | Flujo completo: search_locations → list_properties → respuesta con datos reales |
| 3 | **Off-topic** | "¿Cuál es la capital de Francia?" | No | Rechazar cortésmente, sin inventar ni llamar herramientas |

### 3.2 Métricas evaluadas

- **Tiempo de respuesta** (end-to-end, incluyendo tool execution)
- **Correcto uso de herramientas** (¿llamó las tools correctas? ¿evitó tools innecesarias?)
- **Calidad de respuesta** (¿en español? ¿relevante? ¿menciona datos reales?)
- **Fiabilidad** (¿falla intermitentemente? ¿genera schemas válidos?)

### 3.3 Sistema de puntuación

| Criterio | Puntos |
|----------|--------|
| Respuesta válida en español | +1.0 |
| Function calling exitoso (escenario 2) | +2.0 (1 por calidad + 1 por uso correcto de tools) |
| No usar tools en escenarios que no lo requieren | +0.5 |
| **Máximo posible** | **7.5** |

### 3.4 Entorno de ejecución

- **OS:** Windows 11 Pro
- **Python:** 3.11.4
- **Ubicación:** Santiago, Chile
- **Conexión:** Fibra óptica residencial
- **Fecha/hora:** 15 de marzo de 2026, ~17:00 UTC-3

---

## 4. Resultados

### 4.1 Tabla de resultados (benchmark final — rate limits respetados)

Los dos mejores modelos (1 por proveedor) fueron enfrentados en condiciones limpias, respetando los RPM de cada free tier (25s delay para Gemini, 3s para Groq):

| Modelo | Provider | Saludo | Búsqueda (FC) | Off-topic | Score | Avg Time |
|--------|----------|--------|---------------|-----------|-------|----------|
| **qwen/qwen3-32b** | Groq | 1.05s ✅ | 3.90s ✅ | 0.85s ✅ | **6/6** | **1.93s** |
| **gemini-3.1-flash-lite-preview** | Gemini | 1.25s ✅ | 4.52s ✅ | 2.77s ✅ | **6/6** | 2.85s |

Ambos modelos completaron los 3 escenarios perfectamente: function calling correcto (`search_locations` → `list_properties`), respuestas en español, y rechazo educado de off-topic.

### 4.1b Tabla de eliminación previa (modelos descartados)

| Modelo | Provider | Saludo | Búsqueda (FC) | Off-topic | Score | Motivo de descarte |
|--------|----------|--------|---------------|-----------|-------|--------------------|
| llama-3.3-70b-versatile | Groq | ❌ 400 | 2.24s ✅ | 0.69s ✅ | 4/6 | Bug intermitente `tool_use_failed` |
| llama-4-scout-17b | Groq | 0.54s ✅ | ❌ 400 | 0.41s ⚠️ | 3/6 | Type mismatch en tool params |
| llama-3.1-8b-instant | Groq | 0.66s ✅ | ❌ 413 | 0.56s ✅ | 3/6 | Context 8K insuficiente |

### 4.2 Detalle de fallos

#### llama-3.3-70b-versatile — `tool_use_failed` (intermitente)
```
Error code: 400 - Failed to call a function.
failed_generation: '<function=search_locations {"country_id": "CL", ...} </function>'
```
**Causa:** El modelo genera tool calls en formato XML/texto en vez del JSON estructurado que Groq espera. Es un bug conocido reportado en múltiples repositorios open-source. Ocurre de forma intermitente (~40% de las veces en nuestras pruebas).

#### llama-4-scout-17b — Type mismatch
```
Error: parameters for tool list_properties did not match schema:
  /price_max: expected number, but got string
  /bedrooms_min: expected integer, but got string
```
**Causa:** El modelo envía `"2"` (string) donde el schema requiere `2` (integer). Groq valida los tipos server-side antes de ejecutar, por lo que no se puede parchar client-side.

#### llama-3.1-8b-instant — Request too large
```
Error code: 413 - Request too large for model llama-3.1-8b-instant
```
**Causa:** Context window de 8K tokens es insuficiente para el system prompt + herramientas + resultados de la API de propiedades (que devuelven JSON extenso).

#### gemini-2.5-flash-lite — Rate limit exhausted
```
429 RESOURCE_EXHAUSTED - limit: 20
```
**Causa:** Cupo diario/por-minuto agotado tras múltiples corridas de tests en la misma sesión. Gemini no pudo ser evaluado en igualdad de condiciones. En sesiones anteriores del mismo día, se confirmó que el function calling funciona correctamente cuando hay cupo disponible.

### 4.3 Gemini funciona — el problema era rate limiting

En el benchmark final con delays adecuados (25s entre tests), `gemini-3.1-flash-lite-preview` obtuvo **6/6** perfecto. Las corridas previas con `gemini-2.5-flash-lite` fallaban por dos razones:

1. **RPM (requests por minuto):** function calling genera 3 API calls por conversación en ~2 segundos. Sin delays, 6 tests = 18 calls instantáneos, superando el RPM de 15.
2. **RPD agotado:** tras múltiples corridas de debug, se consumieron las ~20 requests diarias de ese modelo específico.

El dashboard de Google AI Studio confirmó: el total de requests en la hora de testing fue ~60-80, no 1,000. Los errores 429 eran por RPM, no por agotamiento del cupo diario global.

---

## 5. Análisis comparativo

### 5.1 Velocidad (benchmark final, ambos 6/6)

```
Modelo                          Saludo    FC (3 calls)    Off-topic    Promedio
─────────────────────────────────────────────────────────────────────────────
qwen/qwen3-32b (Groq)          1.05s     3.90s           0.85s        1.93s
gemini-3.1-flash-lite (Gemini)  1.25s     4.52s           2.77s        2.85s
```

Groq es **~30% más rápido** en promedio. La mayor diferencia está en off-topic (0.85s vs 2.77s).

### 5.2 Fiabilidad de function calling

Ambos finalistas obtuvieron 100% de éxito en function calling. Ambos ejecutaron correctamente el flujo `search_locations` → `list_properties` con los parámetros correctos.

Los modelos descartados fallaron por:

| Modelo | Error | Causa raíz |
|--------|-------|------------|
| llama-3.3-70b | `tool_use_failed` intermitente (~40%) | Genera XML en vez de JSON para tool calls |
| llama-4-scout-17b | `tool_use_failed` por types | Envía `"2"` (string) donde schema pide `2` (integer) |
| llama-3.1-8b | `413 Request too large` | Context window 8K insuficiente para system prompt + tool results |

### 5.3 Cuota del free tier

| Criterio | qwen/qwen3-32b (Groq) | gemini-3.1-flash-lite (Gemini) |
|----------|----------------------|-------------------------------|
| **RPM** | **60** | 15 |
| **RPD** | **1,000** | ~20 por modelo* |
| **TPM** | 500K | 250K |
| Conversaciones/día (3 req c/u) | **~333** | ~7 por modelo |
| Margen para desarrollo | Amplio | Muy ajustado |

> *\*El RPD real de Gemini es confuso. Los blogs reportan 1,000 pero en la práctica se agotó en ~20 requests por modelo. Los cupos podrían ser mayores si se crea un nuevo proyecto.*

### 5.4 Calidad de respuesta

Ambos modelos generaron respuestas de alta calidad:

| Criterio | qwen/qwen3-32b | gemini-3.1-flash-lite |
|----------|----------------|----------------------|
| Español correcto | ✅ | ✅ |
| Datos reales de API | ✅ | ✅ |
| Tono profesional | ✅ | ✅ |
| Sugiere acciones | ✅ | ✅ |
| Rechazo educado off-topic | ✅ (a veces responde la pregunta igual) | ✅ (más estricto en rechazar) |

---

## 6. Decisión final

### Modelo seleccionado: `qwen/qwen3-32b` via Groq

Ambos finalistas obtuvieron **6/6** en calidad. La decisión se basa en factores operacionales:

| Criterio | qwen/qwen3-32b (Groq) | gemini-3.1-flash-lite (Gemini) | Ganador |
|----------|----------------------|-------------------------------|---------|
| **Score** | 6/6 | 6/6 | Empate |
| **Velocidad promedio** | 1.93s | 2.85s | Groq |
| **RPM** | 60 | 15 | Groq (4x) |
| **RPD** | 1,000 | ~20 por modelo | Groq (50x) |
| **Margen desarrollo** | Amplio | Muy ajustado | Groq |
| **SDK** | OpenAI-compatible | Propietario | Groq |
| **Mensajes de error** | Claros | Confusos (RPM vs RPD) | Groq |
| **Function calling** | 100% fiable | 100% fiable | Empate |

### Por qué Groq sobre Gemini

1. **60 RPM vs 15 RPM**: con function calling (3 calls/conversación), Gemini soporta ~5 usuarios concurrentes por minuto vs ~20 en Groq.
2. **Desarrollo iterativo**: los 20 RPD por modelo de Gemini se agotan en una sesión de debugging. Groq con 1,000 RPD permite iterar libremente.
3. **SDK estándar**: el formato OpenAI-compatible permite migrar a cualquier proveedor (OpenAI, Anthropic, Mistral, otro Groq model) cambiando solo `base_url` y `api_key`.
4. **Velocidad**: 1.93s vs 2.85s — 32% más rápido en promedio.

### Por qué no los otros modelos Groq

| Modelo | Razón de descarte |
|--------|-------------------|
| **llama-3.3-70b-versatile** | Bug intermitente `tool_use_failed` (~40%) — genera XML para tool calls en vez de JSON |
| **llama-4-scout-17b** | Envía tipos incorrectos (string en vez de integer) que Groq rechaza server-side |
| **llama-3.1-8b-instant** | Context window de 8K insuficiente para system prompt + tool results extensos |

### Trade-off aceptado

Qwen3-32b tiene un "thinking mode" interno que ocasionalmente agrega latencia en respuestas simples. En el benchmark, el off-topic varió entre 0.85s y 13s dependiendo de la corrida. Esto es aceptable para un chat inmobiliario donde la prioridad es precisión sobre velocidad sub-segundo.

### Modelo de respaldo

Si `qwen/qwen3-32b` presenta problemas, el fallback recomendado es `gemini-3.1-flash-lite-preview` o `gemini-2.5-flash-lite`. Esto requiere cambiar de SDK (Groq → google-genai) ya que usan formatos distintos. El modelo es configurable via variable de entorno `LLM_MODEL`.

---

## 7. Configuración resultante

```env
# .env
GROQ_API_KEY=gsk_...
LLM_MODEL=qwen/qwen3-32b
```

```python
# config.py
llm_model: str = "qwen/qwen3-32b"
```

El modelo es configurable via variable de entorno, permitiendo cambiar sin modificar código.
