# Decisión de arquitectura: elección de modelo
  
## Modelo elegido
Gemini 3.5 Flash Lite
 
## Diagrama de arquitectura
*(El diagrama de arquitectura de la miniaplicación en formato imagen o PDF se encuentra vinculado en esta misma carpeta, mostrando el flujo de las funciones `armar_peticion`, `enviar_peticion`, `extraer_texto`, el uso de `usageMetadata` y el cálculo de costos).*
 
## Comparación de candidatos

| Criterio | Gemini 3.5 Flash Lite | Gemini 3 Flash Preview |
| :--- | :--- | :--- |
| **C1 (Tokens de entrada / 1M)** | $0,30 USD | $0,50 USD |
| **C2 (Tokens de salida / 1M)** | $2,50 USD | $3,00 USD |
| **C3 (Latencia promedio)** | 2,56 segundos | 6,47 segundos |
| **C4 (Calidad )** | Concisa, directa y cumple adecuadamente con lo solicitado. | Clara y detallada, pero con mayor tiempo de respuesta y mayor tokens de salida. |

## Justificación
Elegí Gemini 3.5 Flash Lite porque  para mi miniaplicación funciona como un asistente ágil y directo, diseñado para ofrecer respuestas rápidas y acotadas. Con una latencia promedio de 2,56 segundos frente a los casi 6 segundos y medio del Modelo Gemini 3 Flash Preview , ofrece una experiencia de usuario mucho más fluida. Además, sus tarifas de entrada ($0,30 USD por millón) y salida ($2,50 USD por millón) son más económicas, lo que optimiza los costos operativos a escala sin sacrificar la calidad de las respuestas en tareas de complejidad baja.
 
## Alternativa descartada y por qué
Descarté Gemini 3 Flash Preview: aunque es un modelo potente, su latencia promedio observada fue significativamente mayor (6,47 segundos), lo que degrada la experiencia en interacciones rápidas. Asimismo, sus costos por token son más elevados ($0,50 USD de entrada y $3,00 USD de salida), y el nivel de detalle adicional que aporta no se justifica para una miniaplicación que prioriza la velocidad de respuesta y la eficiencia de costos.