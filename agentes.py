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
    """Busca fragmentos relevantes dentro del contrato."""
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

    auditor_legal = Agent(
        role="Auditor Legal",
        goal="Identificar riesgos contractuales y clausulas abusivas.",
        backstory="Eres un abogado experto en derecho corporativo para detectar trampas legales.",
        verbose=False,
        # Eliminamos el parámetro llm de aquí
        tools=[buscar_en_contrato],
    )

    asesor_repatriacion = Agent(
        role="Asesor de Relocalizacion",
        goal="Evaluar el impacto del contrato en la vida del trabajador (visados, mudanza).",
        backstory="Experto en movilidad global. Proteges al empleado en el extranjero.",
        verbose=False,
        # Eliminamos el parámetro llm de aquí
    )

    tarea_auditoria = Task(
        description="Localiza las secciones de penalizaciones y rescision. Genera una lista con los 3 riesgos legales mas altos.",
        expected_output="Un informe estructurado detallando los riesgos.",
        agent=auditor_legal,
    )

    tarea_asesoria = Task(
        description="Basandote en el informe del Auditor Legal, explica que le pasaria al visado si es despedido, y propon mejoras.",
        expected_output="Un plan de mitigacion claro.",
        agent=asesor_repatriacion,
    )

    crew = Crew(
        agents=[auditor_legal, asesor_repatriacion],
        tasks=[tarea_auditoria, tarea_asesoria],
        process=Process.sequential,
        verbose=False,
    )

    resultado = crew.kickoff()
    return str(resultado)
