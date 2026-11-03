# Límites de la métrica de evaluación

## Qué mide
Coincidencia de palabras entre una respuesta generada y una
referencia, contando repeticiones (precisión, cobertura, F1).

## Modos de falla conocidos
- **Desajuste de longitud y profundidad (Long Response vs. Short Reference):** Cuando se comparan referencias minimalistas y cortas (ej. ~8 palabras) contra respuestas del modelo largas, ricas, estructuradas y con bloques de código (ej. más de 200 palabras), la **cobertura se mantiene alta**, pero la **precisión colapsa drásticamente**, arrastrando el puntaje F1 a valores muy bajos (F1 < 0.20) a pesar de que la respuesta sea conceptualmente correcta y exhaustiva.
- **Sinónimos y paráfrasis correctas:** Puntúan bajo a pesar de transmitir exactamente el mismo significado (ej. *“El auto es veloz”* vs *“El vehículo es rápido”*).
- **Datos incorrectos (Alucinaciones factoriales):** Fechas, cifras o nombres propios pueden puntuar alto si el resto de la oración coincide (ej. Python creado en *1991* vs *1989*).
- **Negaciones ausentes o alteradas:** Modificar o quitar una sola palabra clave como "no" invierte el significado completo de la oración pero apenas afecta el puntaje F1.
- **Omisión de información clave:** Una respuesta que omite el dato más importante pero conserva palabras secundarias puede obtener un F1 engañosamente alto.

## Muestra revisada
- **Tamaño:** 3 casos reales ejecutados y evaluados contra referencias cortas en el pipeline, complementados con una muestra analítica de casos extremos (F1 mínimo y máximo).
- **Criterio de selección:** Evaluación automatizada de consultas clave sobre Python y análisis de sensibilidad a la longitud de la respuesta.
- **Fecha de revisión:** 2026-09-09.

## Recomendación de uso
- **Cuándo usar:** Utilizar las métricas automáticas (Precisión, Cobertura, F1) exclusivamente para comparar tendencias globales y volumen de rendimiento entre distintas versiones de prompts o modelos, asegurándose de que las referencias tengan un nivel de detalle comparable al de las respuestas esperadas.
- **Cuándo revisar a mano:** Aplicar siempre una revisión cualitativa (rúbrica de corrección factual, completitud y contradicción) cuando las respuestas del modelo sean explicativas o extensas frente a referencias breves, o ante cualquier respuesta que involucre fechas, cifras, nombres propios o variaciones de negación.