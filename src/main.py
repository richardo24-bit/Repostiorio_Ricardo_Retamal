from consumir_gemini import obtener_dato_de_prueba


instruccion_sistema = "Eres un asistente de soporte técnico experto. Responde de forma breve y concisa."
pregunta_usuario = "¿Cómo puedo verificar rapidamente mi codigo de programación?"


resultado = obtener_dato_de_prueba(
        pregunta=pregunta_usuario, 
        system_instruction=instruccion_sistema, 
        
    )
    
print("\n--- RESULTADO OBTENIDO ---")
print(resultado)         