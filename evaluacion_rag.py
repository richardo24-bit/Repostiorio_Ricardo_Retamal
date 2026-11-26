import os
from datetime import date
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

K = 3

# 10 casos etiquetados a mano sobre el corpus de siniestros (doc0 a doc4)
casos_evaluacion = [
    {
        "pregunta": "¿Cuánto plazo tengo para denunciar un siniestro?",
        "ids_relevantes": {"doc0"},
    },
    {
        "pregunta": "¿Por qué medio se ingresa el denuncio de un choque?",
        "ids_relevantes": {"doc0"},
    },
    {
        "pregunta": "¿Qué papeles piden si choqué el auto?",
        "ids_relevantes": {"doc1"},
    },
    {
        "pregunta": "¿Es necesario llevar el padrón y la licencia al día para aprobar daños?",
        "ids_relevantes": {"doc1"},
    },
    {
        "pregunta": "¿Quién revisa el auto para calcular cuánto cuesta arreglarlo?",
        "ids_relevantes": {"doc2"},
    },
    {
        "pregunta": "¿Dónde se hace la evaluación técnica de piezas y reparación?",
        "ids_relevantes": {"doc2"},
    },
    {
        "pregunta": "¿Con quién reclamo si el peritaje se está demorando mucho?",
        "ids_relevantes": {"doc3"},
    },
    {
        "pregunta": "¿A quién se escalan las quejas operativas en atención de siniestros?",
        "ids_relevantes": {"doc3"},
    },
    {
        "pregunta": "¿Qué es lo que tengo que pagar de mi bolsillo al usar el seguro?",
        "ids_relevantes": {"doc4"},
    },
    {
        # Caso fuera del corpus para validar el n/a en recall
        "pregunta": "¿El seguro cubre robo de accesorios dentro del estacionamiento?",
        "ids_relevantes": set(),
    },
]


def precision_at_k(ids_recuperados, ids_relevantes):
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)


def recall_at_k(ids_recuperados, ids_relevantes):
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)


def promediar(valores):
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0


def evaluar_recuperacion(retriever, casos, k=3):
    resultados = []
    for caso in casos:
        chunks = retriever.invoke(caso["pregunta"])
        ids_recuperados = [c.id for c in chunks][:k]
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({"pregunta": caso["pregunta"], "precision": p, "recall": r})

    precision_promedio = promediar(x["precision"] for x in resultados)
    recall_promedio = promediar(x["recall"] for x in resultados)
    return resultados, precision_promedio, recall_promedio


embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma(
    persist_directory=os.path.abspath("vectorstore"),
    embedding_function=embeddings,
)
retriever = vectorstore.as_retriever(search_kwargs={"k": K})

resultados, precision_promedio, recall_promedio = evaluar_recuperacion(
    retriever, casos_evaluacion, k=K
)

for r in resultados:
    recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
    print(f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}")

print(f"\npromedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}")

with open("resultados_evaluacion.txt", "w", encoding="utf-8") as archivo:
    archivo.write(f"Fecha: {date.today()}\n")
    archivo.write(f"Configuracion: k={K}, chunk_size=200, chunk_overlap=30\n\n")
    for r in resultados:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        archivo.write(f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}\n")
    archivo.write(
        f"\npromedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}\n"
    )

print("\nResultados guardados en resultados_evaluacion.txt")