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

# 📁 Physical path to store the Vector Database on the server
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")


# =====================================================================
# VECTOR SEARCH TOOL (RAG)
# =====================================================================
@tool("Buscar en el Contrato")
def buscar_en_contrato(query: str) -> str:
    """Searches for relevant fragments within the persistent vector database of the contract."""
    # Verify if the database actually exists before querying it
    if not os.path.exists(PERSIST_DIR) or not os.listdir(PERSIST_DIR):
        return "Error: The vector database does not contain indexed information."

    # Load Chroma pointing directly to the persistent directory
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)

    # Accent cleaning to optimize semantic matching
    query_limpia = (
        query.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

    # Retrieve the 3 most similar text fragments
    resultados = db.similarity_search(query_limpia, k=3)
    return "\n---\n".join([doc.page_content for doc in resultados])


# =====================================================================
#  CORE EXECUTION ENGINE
# =====================================================================
def ejecutar_analisis(texto_contrato: str) -> str:
    os.environ["CONTRATO_ACTUAL_TEXTO"] = texto_contrato

    # 1️⃣ PREVIOUS SESSION CLEANING (Prevents mixing fragments from old contracts)
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
    os.makedirs(PERSIST_DIR, exist_ok=True)

    # 2️⃣ INDEXING PHASE (Persistent Storage on Disk)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Segment the text into chunks with overlap to maintain context
    lineas = texto_contrato.split("\n")
    chunks = ["\n".join(lineas[i : i + 15]) for i in range(0, len(lineas), 10)]

    # Initialize Chroma and save vectors to the physical path
    db = Chroma.from_texts(
        texts=chunks, embedding=embeddings, persist_directory=PERSIST_DIR
    )
    db.persist()  # Ensures immediate write to Render's hard drive

    # =====================================================================
    # 🕵️‍♂️ AGENT 1: THE LEGAL AUDITOR
    # =====================================================================
    auditor_legal = Agent(
        role="Senior International Contract Legal Auditor",
        goal="Identify with surgical precision abusive clauses, hidden financial penalties, aggressive exclusivities, and legal loopholes in the contract text.",
        backstory="""You are an elite attorney expert in European corporate and commercial law, specializing in B2B and employment contracts (such as the Polish Civil Code - Kodeks Cywilny). 
        Your obsession is finding exact fine amounts, disproportionate intellectual property clauses, and dangerous notice periods. 
        You assume nothing; you use your semantic search tool to audit the document line by line to extract hard data and textual quotes.
        CRITICAL: You must think, analyze, and write your responses completely in English.""",
        verbose=True,
        tools=[buscar_en_contrato],
    )

    # =====================================================================
    # 🌍 AGENT 2: THE RELOCATION ADVISOR
    # =====================================================================
    asesor_repatriacion = Agent(
        role="Senior Global Mobility and Immigration Advisor",
        goal="Evaluate the real impact of the contract on the professional's immigration status, work visa, relocation process, and their future Karta Pobytu.",
        backstory="""You are a specialist in foreign affairs and international mobility, with deep knowledge of immigration office criteria in the European Union (such as the Mazowiecki Urząd Wojewódzki in Warsaw). 
        You take the findings of the Legal Auditor and dictate whether the salary, working hours, type of contract, and termination clauses jeopardize the employee's immigration stability or block a legal residence procedure abroad.
        CRITICAL: You must think, analyze, and write your final report completely in English.""",
        verbose=True,
    )

    # =====================================================================
    # 📋 SEQUENTIAL TASKS ASSIGNMENT (Stable HTML Layout)
    # =====================================================================
    tarea_auditoria = Task(
        description="""Use the semantic search tool to locate sections regarding penalties, intellectual property, and contract termination. 
        Generate a technical list with the highest legal risks found, citing the exact amounts or textual conditions detected. 
        The entire analysis must be written strictly in English.""",
        expected_output="A technical and detailed report structuring the specific risks and penalties of the contract written entirely in English.",
        agent=auditor_legal,
    )

    tarea_asesoria = Task(
        description="""Based on the Legal Auditor's report, evaluate the impact on relocation visas and job stability. 
        Draft real solutions and legal counterproposals ready to be used to negotiate with the company.
        STRICT REQUIREMENT: The output text must be written entirely in English, but it must be wrapped inside the requested HTML layout containers.""",
        expected_output="""An executive report structured strictly into two main HTML blocks using the frontend utility classes. All text inside must be written in English:
        
        1. Inside '<div class="caja-verde-segura">' (Impact Analysis):
           - Type of contract detected and applicable laws (e.g., Kodeks Cywilny).
           - The 3 most critical risks found, citing the specific amount or context (e.g., 'Penalty of X amount').
           - Relocation Diagnosis: Does this contract support a stable residence application, or does it trigger immigration red flags?
           
        2. Inside '<div class="caja-azul-segura">' (Strategic Mitigation Framework):
           - Exact counterproposals: Alternative legal text ready to copy, paste, and send to the company to negotiate and amend the discovered risks.
           - Bullet points listing immediate strategic actions the professional should execute.""",
        agent=asesor_repatriacion,
    )

    # =====================================================================
    # 🚀 LAUNCH THE CREW WORKFLOW
    # =====================================================================
    crew = Crew(
        agents=[auditor_legal, asesor_repatriacion],
        tasks=[tarea_auditoria, tarea_asesoria],
        process=Process.sequential,
        verbose=True,
    )

    resultado = crew.kickoff()
    return str(resultado)
