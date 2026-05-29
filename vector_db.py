import os
from openai import OpenAI
import faiss
import numpy as np

# Inicializamos el cliente de OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Inicializamos el índice de FAISS en memoria global (dimensión 1536 para OpenAI)
dimension = 1536
index = faiss.IndexFlatL2(dimension)

# Diccionario en memoria para asociar la posición del vector con el texto real
fragmentos_memoria = {}


def obtener_embedding(texto: str, modelo="text-embedding-3-small"):
    """Genera el vector numérico de un texto usando OpenAI"""
    texto = texto.replace("\n", " ")
    respuesta = client.embeddings.create(input=[texto], model=modelo)
    return respuesta.data[0].embedding


def almacenar_contrato_vectorial(nombre_archivo: str, texto_completo: str):
    """Fragmenta el contrato y guarda los vectores directamente en la memoria FAISS"""
    global index, fragmentos_memoria

    # Limpiamos el índice anterior para enfocarnos solo en el contrato actual
    index = faiss.IndexFlatL2(dimension)
    fragmentos_memoria.clear()

    # Fragmentamos el texto en bloques de ~1000 caracteres
    tamano_bloque = 1000
    fragmentos = [
        texto_completo[i : i + tamano_bloque]
        for i in range(0, len(texto_completo), tamano_bloque)
    ]

    vectores = []
    contador = 0

    for frag in fragmentos:
        if frag.strip():
            embedding = obtener_embedding(frag)
            vectores.append(embedding)
            # Guardamos el texto usando el índice numérico como llave
            fragmentos_memoria[contador] = frag
            contador += 1

    if vectores:
        # Convertimos la lista de vectores a un array de numpy tipo float32 (lo que exige FAISS)
        vectores_np = np.array(vectores).astype("float32")
        index.add(vectores_np)


def consultar_vectores_similes(query: str, limite=3):
    """Busca los fragmentos de texto más relevantes usando el índice FAISS en memoria"""
    global index, fragmentos_memoria

    if index.ntotal == 0:
        return "No hay datos indexados en el contrato actualmente."

    embedding_query = obtener_embedding(query)
    query_np = np.array([embedding_query]).astype("float32")

    # Buscamos las distancias y los índices de los fragmentos más cercanos
    distancias, indices = index.search(query_np, limite)

    fragmentos_encontrados = []
    for idx in indices[0]:
        if idx in fragmentos_memoria:
            fragmentos_encontrados.append(fragmentos_memoria[idx])

    texto_contexto = "\n---\n".join(fragmentos_encontrados)
    return (
        texto_contexto if texto_contexto else "No se encontraron fragmentos relevantes."
    )
