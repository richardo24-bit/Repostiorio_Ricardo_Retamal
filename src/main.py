from consumir_gemini import obtener_dato_de_prueba


instruccion_sistema = "Eres un experto en aviación. Responde de forma breve y concisa."
pregunta_usuario = "¿Por que vuelan los aviones?"


resultado = obtener_dato_de_prueba(
        pregunta=pregunta_usuario, 
        system_instruction=instruccion_sistema, 
        
    )
    
print("\n--- RESULTADO OBTENIDO ---")
print(resultado)         