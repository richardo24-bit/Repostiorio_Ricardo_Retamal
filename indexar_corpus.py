import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit("Falta la GEMINI_API_KEY en el .env")

corpus = [
    "El denuncio de un siniestro automotriz debe realizarse idealmente dentro de las primeras 48 horas de ocurrido el hecho mediante el formulario oficial.",
    "Para la aprobación de daños materiales en choques, el asegurado debe presentar su licencia de conducir vigente, el padrón del vehículo y el relato firmado.",
    "El proceso de liquidación incluye la evaluación del vehículo en un taller colaborador para determinar el presupuesto técnico de reparación y sustitución de piezas.",
    "Las quejas operativas o demoras excesivas en los plazos de peritaje deben ser escaladas al supervisor de calidad mediante el flujo interno de atención.",
    "El deducible es un monto estipulado en la póliza que asume el asegurado sobre el valor total de los daños de su vehículo al momento del siniestro.",
]

# Cada doc lleva su fuente para poder citarla despues
metadatas = [
    {"fuente": "manual_denuncios.md"},
    {"fuente": "requisitos_choques.md"},
    {"fuente": "proceso_liquidacion.md"},
    {"fuente": "protocolo_reclamos.md"},
    {"fuente": "glosario_poliza.md"},
]

# IDs fijos (sirven para la evaluacion del Bloque 27)
ids = [f"doc{i}" for i in range(len(corpus))]

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
chunks = splitter.create_documents(corpus, metadatas=metadatas)

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
persist_dir = os.path.abspath("vectorstore")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    ids=ids,
    persist_directory=persist_dir,
)

print(f"Reindexados {len(chunks)} chunks con metadata e ids en {persist_dir}")