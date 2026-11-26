import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# 1. Corpus de ejemplo (política de devoluciones)
corpus_ejemplo = [
    "Los pedidos se pueden cancelar dentro de las primeras 24 horas despues de "
    "realizados, sin costo adicional.",
    "Las devoluciones se aceptan hasta 30 dias despues de la entrega, siempre que "
    "el producto este sin usar.",
    "El reembolso se procesa en un plazo de 5 a 10 dias habiles despues de recibir "
    "el producto devuelto.",
    "Los productos en oferta o liquidacion no tienen devolucion, salvo defecto de "
    "fabrica.",
    "El envio de una devolucion corre por cuenta del cliente, excepto cuando el "
    "producto llego danado.",
]

# 2. Chunking recursivo (chunk_size=150, chunk_overlap=20)
splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
chunks = splitter.create_documents(corpus_ejemplo)

print(f"{len(chunks)} chunks generados")
for i, chunk in enumerate(chunks):
    print(f"--- chunk {i} ({len(chunk.page_content)} caracteres) ---")
    print(chunk.page_content)

# Paso extra: verificar integridad local antes de llamar a la API
vacios = [i for i, c in enumerate(chunks) if not c.page_content.strip()]
textos = [c.page_content for c in chunks]
hay_duplicados = len(textos) != len(set(textos))
total_chars_chunks = sum(len(c.page_content) for c in chunks)
total_chars_corpus = sum(len(d) for d in corpus_ejemplo)

print("\n--- Verificación de integridad ---")
print("chunks vacios:", vacios)
print("hay duplicados:", hay_duplicados)
print("total de caracteres en los chunks:", total_chars_chunks)
print("total de caracteres en el corpus original:", total_chars_corpus)

# 3 y 4. Embeddings e indexación en Chroma (en carpeta y colección separadas)
load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit('Falta GEMINI_API_KEY. Defínela en tu archivo ".env" y vuelve a ejecutar.')

PERSIST_DIR = os.path.abspath("vectorstore_ejemplo")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

try:
    vectorstore_ejemplo = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="corpus_ejemplo",
        persist_directory=PERSIST_DIR,
    )
except Exception as error:
    mensaje = str(error)
    if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
        print("Límite de peticiones alcanzado. Espera un minuto y vuelve a ejecutar.")
    elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
        print('La API rechazó tu clave. Revisa el valor de GEMINI_API_KEY en tu ".env".')
    else:
        print("No se pudo indexar el corpus:", type(error).__name__)
    print("Detalle técnico:", mensaje)
    raise SystemExit(1)

print(f"\nIndexados {len(chunks)} chunks en {PERSIST_DIR}")

# 5. Verificar persistencia reconectando desde cero
vectorstore_ejemplo_recargado = Chroma(
    collection_name="corpus_ejemplo",
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings,
)
print("Chunks recargados desde disco:", vectorstore_ejemplo_recargado._collection.count())