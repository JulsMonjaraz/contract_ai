import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

# FIX PYDANTIC: Configuramos el modelo de manera nativa para CrewAI
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"


@tool("Buscar en el Contrato")
def buscar_en_contrato(query: str) -> str:
    """Busca fragmentos relevantes dentro del contrato utilizando base de datos vectorial."""
    texto_contrato = os.environ.get("CONTRATO_ACTUAL_TEXTO", "")

    if not texto_contrato:
        return "No hay ningun contrato cargado."

    lineas = texto_contrato.split("\n")
    chunks = ["\n".join(lineas[i : i + 15]) for i in range(0, len(lineas), 10)]

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma.from_texts(chunks, embeddings)

    query_limpia = (
        query.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    resultados = db.similarity_search(query_limpia, k=3)

    return "\n---\n".join([doc.page_content for doc in resultados])


def ejecutar_analisis(texto_contrato: str) -> str:
    os.environ["CONTRATO_ACTUAL_TEXTO"] = texto_contrato

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
        backstory="""Eres un especialista en extranjería y movilidad internacional, con conocimiento profundo de los criterios de las oficinas de inmigración en la Unión Europea (como el Mazowiecki Urząd Wojewódzki en Varsovia). 
        Tomas los hallazgos del Auditor Legal y dictaminas si el salario, las horas, el tipo de contrato y las cláusulas de rescisión ponen en riesgo la estabilidad migratoria del empleado o si bloquean un trámite de residencia legal en el extranjero.""",
        verbose=True,
    )

    # =====================================================================
    # 📋 TAREAS
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
    # 🚀 ORQUESTACIÓN DE LA CREW
    # =====================================================================
    crew = Crew(
        agents=[auditor_legal, asesor_repatriacion],
        tasks=[tarea_auditoria, tarea_asesoria],
        process=Process.sequential,
        verbose=True,
    )

    resultado = crew.kickoff()
    return str(resultado)
