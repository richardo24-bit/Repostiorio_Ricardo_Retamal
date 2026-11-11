import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# 1. Cargar las variables del archivo .env
load_dotenv()

# 2. Verificar la clave antes de llamar a la API
if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit('Falta GEMINI_API_KEY. Defínela en tu archivo ".env" y vuelve a ejecutar.')

# 3. Inicializar el modelo de embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# 4. Prueba rápida de embedding unitario para verificar conectividad
try:
    vector = embeddings.embed_query("El cliente reintenta ante un error")
    print("Longitud del vector de prueba:", len(vector))
    print("Primeros 5 valores del vector:", vector[:5])
except Exception as error:
    mensaje = str(error)
    if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
        print("Límite de peticiones alcanzado. Espera un minuto y vuelve a ejecutar.")
    elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
        print('La API rechazó tu clave. Revisa el valor de GEMINI_API_KEY en tu ".env".')
    else:
        print("No se pudo generar el embedding:", type(error).__name__)
    print("Detalle técnico:", mensaje)
    raise SystemExit(1)

# 5. Definición del corpus propio de siniestros automotrices
corpus = [
    "El denuncio de un siniestro automotriz debe realizarse idealmente dentro de las primeras 48 horas de ocurrido el hecho mediante el formulario oficial.",
    "Para la aprobación de daños materiales en choques, el asegurado debe presentar su licencia de conducir vigente, el padrón del vehículo y el relato firmado.",
    "El proceso de liquidación incluye la evaluación del vehículo en un taller colaborador para determinar el presupuesto técnico de reparación y sustitución de piezas.",
    "Las quejas operativas o demoras excesivas en los plazos de peritaje deben ser escaladas al supervisor de calidad mediante el flujo interno de atención.",
    "El deducible es un monto estipulado en la póliza que asume el asegurado sobre el valor total de los daños de su vehículo al momento del siniestro."
]

# 6. Aplicar Chunking (Estrategia Recursiva)
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
chunks = splitter.create_documents(corpus)
print(f"\nTexto fragmentado en {len(chunks)} chunks.")

# 7. Indexación y persistencia de embeddings en el Vector Store (Chroma)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="vectorstore/",
)

print(f"¡Indexación completada con éxito! {len(chunks)} chunks almacenados en 'vectorstore/'.")

# 8. Verificación de lectura e integridad posterior
vectorstore_recargado = Chroma(
    persist_directory="vectorstore/",
    embedding_function=embeddings,
)
print(f"Verificación de persistencia: El vector store contiene {vectorstore_recargado._collection.count()} elementos.")