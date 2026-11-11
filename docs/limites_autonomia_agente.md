# Límites de autonomía: Asistente de Orientación y Siniestros

## Herramientas y nivel de riesgo
- **consultar_pasos_a_seguir:** Bajo (herramienta de solo lectura informativa; guía al cliente en los procesos internos sin modificar registros de póliza).
- **consultar_documentacion_aprobacion:** Bajo (herramienta de consulta documental; lista requisitos legales y técnicos necesarios para la tramitación).
- **escalar_queja_operativa_a_supervisor:** Alto (herramienta de registro e intervención en el flujo de atención para casos de alta insatisfacción o reclamos formales que requieren derivación humana prioritaria).

## Herramientas que requieren aprobación humana
- **escalar_queja_operativa_a_supervisor:** Las quejas complejas o solicitudes de compensación extraordinaria detectadas por el agente requieren una validación humana posterior en el panel de soporte para garantizar una respuesta coordinada con el área de calidad de servicio.

## Revisión de trazas
- **Frecuencia:** Semanal.
- **Qué se busca:** 
  - Verificar que las respuestas explicativas sobre pasos y documentos sean precisas y no omitan requisitos legales clave.
  - Revisar el tono del agente ante consultas y quejas de clientes para asegurar empatía y contención adecuada.
  - Asegurar que las herramientas invocadas correspondan al contexto de la consulta (por ejemplo, que no se confundan trámites de choques con siniestros de robo).

## Qué hacer ante un comportamiento inesperado
1. **Ajustar los esquemas de Pydantic o docstrings** si el agente selecciona de manera incorrecta entre pasos a seguir o documentación requerida.
2. **Revisar las trazas guardadas** en `trazas_agente.jsonl` para identificar si el modelo respondió de forma ambigua a las quejas planteadas por los usuarios.
3. **Actualizar la base de conocimiento interna** de las herramientas si los protocolos operativos o la documentación legal de la compañía cambian.