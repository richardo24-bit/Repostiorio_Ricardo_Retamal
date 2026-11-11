from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

# Texto de prueba relacionado con nuestro dominio de seguros y siniestros
texto = (
    "El denuncio de un siniestro automotriz debe realizarse idealmente dentro de "
    "las primeras 48 horas de ocurrido el hecho mediante el formulario oficial.\n\n"
    "Para la aprobación de daños materiales en choques, el asegurado debe presentar "
    "su licencia de conducir vigente, el padrón del vehículo y el relato firmado.\n\n"
    "El proceso de liquidación incluye la evaluación del vehículo en un taller colaborador "
    "para determinar el presupuesto técnico de reparación y sustitución de piezas."
)

print("=== 1. CHUNKING DE TAMAÑO FIJO ===")
splitter_fijo = CharacterTextSplitter(separator="", chunk_size=120, chunk_overlap=0)
chunks_fijo = splitter_fijo.split_text(texto)

for i, chunk in enumerate(chunks_fijo):
    print(f"\n--- Chunk Fijo {i} ({len(chunk)} caracteres) ---")
    print(chunk)

print("\n\n=== 2. CHUNKING RECURSIVO ===")
splitter_recursivo = RecursiveCharacterTextSplitter(chunk_size=120, chunk_overlap=20)
chunks_recursivo = splitter_recursivo.split_text(texto)

for i, chunk in enumerate(chunks_recursivo):
    print(f"\n--- Chunk Recursivo {i} ({len(chunk)} caracteres) ---")
    print(chunk)