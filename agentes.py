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
    # 🕵️‍♂️ AGENTE 1: EL AUDITOR LEGAL (Cazador de trampas y números exactos)
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
    # 🌍 AGENTE 2: EL ASESOR DE RELOCALIZACIÓN (Especialista en Visados y Karta Pobytu)
    # =====================================================================
    asesor_repatriacion = Agent(
        role="Asesor Senior de Movilidad Global e Inmigración",
        goal="Evaluar el impacto real del contrato sobre el estatus migratorio del profesional, su visado de trabajo, reubicación y su futura Karta Pobytu.",
        backstory="""Eres un especialista en extranjería y movilidad internacional, con conocimiento profundo de los criterios de las oficinas de inmigración en la Unión Europea (como el Mazowiecki Urząd Wojewódzki en Varsovia). 
        Tomas los hallazgos del Auditor Legal y dictaminas si el salario, las horas, el tipo de contrato y las cláusulas de rescisión ponen en riesgo la estabilidad migratoria del empleado o si bloquean un trámite de residencia legal en el extranjero.""",
        verbose=True,
    )

    # =====================================================================
    # 📋 TAREAS (Asignación secuencial de objetivos específicos)
    # =====================================================================
    tarea_auditoria = Task(
        description="""Utiliza la herramienta de búsqueda semántica para localizar exhaustivamente las secciones de penalizaciones, propiedad intelectual y rescisión. 
        Genera una lista técnica con los riesgos legales más altos encontrados, citando montos o condiciones textuales detectadas.""",
        expected_output="Un informe técnico y detallado estructurando los riesgos y penalizaciones específicas del contrato.",
        agent=auditor_legal,
    )

    tarea_asesoria = Task(
        description="""Basándote en el informe del Auditor Legal, evalúa el impacto en los visados de reubicación y estabilidad laboral. 
        Redacta soluciones reales y contrapropuestas legales listas para negociar con la empresa.""",
        expected_output="""Tu respuesta debe ser TEXTO PLANO DIRECTO. PROHIBIDO usar bloques de código Markdown con la palabra ```html o ```. PROHIBIDO inventar títulos iniciales. Entrega exactamente este formato:

Escribe aquí directamente el contenido de los riesgos, leyes aplicables (ej. Kodeks Cywilny) y el diagnóstico migratorio detallado para la Karta Pobytu. No pongas etiquetas HTML contenedoras.

plan de mitigación:
Escribe aquí el plan de mitigación detallado, las acciones inmediatas y las plantillas de correo exactas para renegociar las cláusulas abusivas encontradas.

CRÍTICO: La frase exacta 'plan de mitigación:' (en minúsculas y con dos puntos) DEBE separar ambos bloques para que el sistema funcione.""",
        agent=asesor_repatriacion,
    )

    # =====================================================================
    # 🚀 ORQUESTACIÓN DE LA CREW
    # =====================================================================
    crew = Crew(
        agents=[auditor_legal, asesor_repatriacion],
        tasks=[
            tarea_auditoria,
            tarea_asesoria,
        ],  # 🛠️ CORREGIDO: Ahora coincide exactamente con tus variables
        process=Process.sequential,
        verbose=True,  # Lo dejamos en True para que puedas auditar en la consola de Render qué hace cada agente
    )

    resultado = crew.kickoff()
    return str(resultado)
