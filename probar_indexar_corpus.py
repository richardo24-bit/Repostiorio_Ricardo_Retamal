import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# 1. Cargar variables de entorno
load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit('Falta GEMINI_API_KEY en el archivo ".env".')

# 2. Inicializar el mismo modelo de embeddings que usaste para indexar
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# 3. Conectarse al vector store existente en disco (sin re-indexar)
vectorstore = Chroma(
    persist_directory="vectorstore/",
    embedding_function=embeddings,
)

print(f"Total de chunks recuperables en el índice: {vectorstore._collection.count()}")

# 4. Definir una pregunta de prueba (fíjate que usa otras palabras que el corpus original)
pregunta = "¿Qué pasa si me demoro mucho en reportar el choque de mi auto?"

print(f"\nPregunta de búsqueda: '{pregunta}'\n")

# 5. Buscar los chunks más relevantes por similitud semántica
resultados = vectorstore.similarity_search(pregunta, k=2)

print("--- RESULTADOS RECUPERADOS ---")
for i, doc in enumerate(resultados):
    print(f"\n[Resultado {i+1}]")
    print(doc.page_content)