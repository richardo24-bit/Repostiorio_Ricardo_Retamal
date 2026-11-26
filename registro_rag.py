import os
import time
import json
from contextlib import contextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
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
    for i, doc in enumerate(chunks_recuperados, start=1):
        lineas.append(f"[{i}] {doc.page_content}")
    return "\n\n".join(lineas)


@contextmanager
def medir(tiempos, etapa):
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio


def registrar_consulta(pregunta, persist_directory, k=3):
    tiempos = {}

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    chat_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    with medir(tiempos, "embed_y_busqueda"):
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        chunks = retriever.invoke(pregunta)

    contexto = formatear_contexto(chunks)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    with medir(tiempos, "generacion"):
        respuesta = chat_model.invoke(prompt)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": dict(respuesta.usage_metadata) if respuesta.usage_metadata else None,
    }


if __name__ == "__main__":
    ruta_indice = os.path.abspath("vectorstore")

    # 3 preguntas del Bloque 27 con k=3, mas la primera repetida con k=6
    # (como el corpus tiene 5 docs, k=6 trae los 5 y igual sube input_tokens)
    pruebas = [
        ("¿Cuánto plazo tengo para denunciar un siniestro?", 3),
        ("¿Qué papeles piden si choqué el auto?", 3),
        ("¿Qué es lo que tengo que pagar de mi bolsillo al usar el seguro?", 3),
        ("¿Cuánto plazo tengo para denunciar un siniestro?", 6),
    ]

    with open("registros_latencia_costo.jsonl", "a", encoding="utf-8") as f:
        for pregunta, k in pruebas:
            registro = registrar_consulta(pregunta, persist_directory=ruta_indice, k=k)
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")

            tokens_in = registro["tokens"]["input_tokens"] if registro["tokens"] else None
            t_busq = registro["tiempos_ms"]["embed_y_busqueda"]
            t_gen = registro["tiempos_ms"]["generacion"]
            print(f"k={k} | input_tokens={tokens_in} | busq={t_busq}ms | gen={t_gen}ms | {pregunta[:40]}")