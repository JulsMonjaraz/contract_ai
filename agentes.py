import os
import shutil
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

# FIX PYDANTIC & TELEMETRY
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

# 📁 Ruta física para almacenar la Base de Datos Vectorial en el servidor
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")


# =====================================================================
# HERRAMIENTA DE BÚSQUEDA VECTORIAL (RAG)
# =====================================================================
@tool("Buscar en el Contrato")
def buscar_en_contrato(query: str) -> str:
    """Busca fragmentos relevantes dentro de la base de datos vectorial persistente del contrato."""
    # Verificamos si la base de datos realmente existe antes de consultarla
    if not os.path.exists(PERSIST_DIR) or not os.listdir(PERSIST_DIR):
        return "Error: La base de datos vectorial no contiene información indexada."

    # Cargamos Chroma apuntando directamente al directorio persistente
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)

    # Limpieza de acentos para optimizar la coincidencia semántica
    query_limpia = (
        query.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

    # Recuperamos los 3 fragmentos de texto más similares
    resultados = db.similarity_search(query_limpia, k=3)
    return "\n---\n".join([doc.page_content for doc in resultados])


# =====================================================================
#  MOTOR PRINCIPAL DE EJECUCIÓN
# =====================================================================
def ejecutar_analisis(texto_contrato: str) -> str:
    os.environ["CONTRATO_ACTUAL_TEXTO"] = texto_contrato

    # 1️⃣ LIMPIEZA DE SESIÓN ANTERIOR (Evita que se mezclen fragmentos de contratos viejos)
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
    os.makedirs(PERSIST_DIR, exist_ok=True)

    # 2️⃣ FASE DE INDEXACIÓN (Guardado Persistente en Disco)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Segmentamos el texto en trozos con solapamiento (Overlap) para no perder contexto
    lineas = texto_contrato.split("\n")
    chunks = ["\n".join(lineas[i : i + 15]) for i in range(0, len(lineas), 10)]

    # Inicializamos Chroma y guardamos los vectores en la ruta física
    db = Chroma.from_texts(
        texts=chunks, embedding=embeddings, persist_directory=PERSIST_DIR
    )
    db.persist()  # Asegura la escritura inmediata en el disco duro de Render

    # =====================================================================
    # 🕵️‍♂️ AGENTE 1: EL AUDITOR LEGAL
    # =====================================================================
    auditor_legal = Agent(
        role="Auditor Legal Senior de Contratos Internacionales",
        goal="Identificar con precisión quirúrgica cláusulas abusivas, penalizaciones financieras ocultas, exclusividades agresivas y vacíos legales en el texto del contrato.",
        backstory="""Eres un abogado de élite experto en derecho corporativo y comercial europeo, especializado en contratos B2B y laborales (como el Código Civil Polaco - Kodeks Cywilny). 
        Tu obsesión es encontrar montos exactos de multas, cláusulas desproporcionadas de propiedad intelectual y periodos de preaviso (Notice Periods) peligrosos. 
        No asumes nada; usas tu herramienta de búsqueda semántica para auditar el documento línea por línea y extraer datos duros y cotizaciones textuales.""",
        verbose=True,
        tools=[buscar_en_contrato],
    )

    # =====================================================================
    # 🌍 AGENTE 2: EL ASESOR DE RELOCALIZACIÓN
    # =====================================================================
    asesor_repatriacion = Agent(
        role="Asesor Senior de Movilidad Global e Inmigración",
        goal="Evaluar el impacto real del contrato sobre el estatus migratorio del profesional, su visado de trabajo, reubicación y su futura Karta Pobytu.",
        backstory="""Eres un especialista en extranjería y movilidad internacional, con conocimiento profundo de los criterios de las oficinas de inmigración en la Unión Europea (como el Mazowiecki Urząd Wojewöhnia en Varsovia). 
        Tomas los hallazgos del Auditor Legal y dictaminas si el salario, las horas, el tipo de contrato y las cláusulas de rescisión ponen en riesgo la estabilidad migratoria del empleado o si bloquean un trámite de residencia legal en el extranjero.""",
        verbose=True,
    )

    # =====================================================================
    # 📋 ASIGNACIÓN DE TAREAS SECUENCIALES (Layout HTML Estable)
    # =====================================================================
    tarea_auditoria = Task(
        description="""Utiliza la herramienta de búsqueda semántica para localizar las secciones de penalizaciones, propiedad intelectual y rescisión. 
        Genera una lista técnica con los riesgos legales más altos encontrados, citando montos o condiciones textuales detectadas.""",
        expected_output="Un informe técnico y detallado estructurando los riesgos y penalizaciones específicas del contrato.",
        agent=auditor_legal,
    )

    tarea_asesoria = Task(
        description="""Basándote en el informe del Auditor Legal, evalúa el impacto en los visados de reubicación y estabilidad laboral. 
        Redacta soluciones reales y contrapropuestas legales listas para negociar con la empresa.""",
        expected_output="""Un informe ejecutivo estructurado estrictamente en dos bloques principales de HTML utilizando las clases del frontend:
        
        1. En '<div class="caja-verde-segura">' (Análisis de Impacto):
           - Tipo de contrato detectado y leyes aplicables (ej. Kodeks Cywilny).
           - Los 3 riesgos más críticos encontrados, citando el monto o contexto (ej. 'Multa de X cantidad').
           - Diagnóstico de reubicación: ¿Este contrato sirve para tramitar una residencia estable o tiene banderas rojas?
           
        2. En '<div class="caja-azul-segura">' (Strategic Mitigation Framework):
           - Contrapropuestas exactas: Texto alternativo legal listo para copiar, pegar y enviar a la empresa para negociar y corregir los riesgos hallados.
           - Viñetas con las acciones inmediatas que debe tomar el profesional.""",
        agent=asesor_repatriacion,
    )

    # =====================================================================
    # 🚀 ENTRADA EN ACCIÓN DE LA CREW
    # =====================================================================
    crew = Crew(
        agents=[auditor_legal, asesor_repatriacion],
        tasks=[tarea_auditoria, tarea_asesoria],
        process=Process.sequential,
        verbose=True,
    )

    resultado = crew.kickoff()
    return str(resultado)
