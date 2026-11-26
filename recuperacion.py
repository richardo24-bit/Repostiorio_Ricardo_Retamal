import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def formatear_contexto(chunks_recuperados):
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente
    return "\n\n".join(lineas), citas


def construir_prompt(pregunta, persist_directory, k=3):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    chunks_recuperados = retriever.invoke(pregunta)
    contexto, citas = formatear_contexto(chunks_recuperados)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
    return prompt, citas


if __name__ == "__main__":
    ruta_indice = os.path.abspath("vectorstore")

    # Probamos con dos preguntas distintas para ver que el contexto cambia
    preguntas = [
        "¿Qué documentos tengo que llevar si choqué el auto?",
        "¿Qué es lo que tengo que pagar yo de mi bolsillo en un siniestro?",
    ]

    for pregunta in preguntas:
        prompt, citas = construir_prompt(pregunta, persist_directory=ruta_indice, k=3)
        print("=" * 60)
        print(prompt)
        print("\nMapa de citas:", citas)