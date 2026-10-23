from consumir_gemini import obtener_dato_de_prueba


instruccion_sistema = "Eres un experto cineasta mundial. Responde de forma breve y concisa."
pregunta_usuario = "¿Cuales son los mejores estrenos en octubre 2026?"


resultado = obtener_dato_de_prueba(
        pregunta=pregunta_usuario, 
        system_instruction=instruccion_sistema, 
        
    )
    
print("\n--- RESULTADO OBTENIDO ---")
print(resultado)         