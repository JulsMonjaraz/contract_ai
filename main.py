import asyncio  # 👈 Librería de asincronismo nativa
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agentes import ejecutar_analisis

# Importamos el cliente oficial de Supabase
from supabase import create_client, Client

load_dotenv(override=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2️⃣ Inicializamos el cliente de Supabase asegurando el tipo 'str' para Pylance
SUPABASE_URL = os.getenv("SUPABASE_URL") or ""
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or ""

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ ¡Alerta! Faltan las credenciales de Supabase en el archivo .env")

# Al usar 'or ""' arriba, garantizamos que create_client reciba un str y no un None
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Nombre exacto de tu tabla en Supabase (Cámbialo si tu tabla se llama distinto)
TABLA_HISTORIAL = "tu_tabla_de_supabase"


class ContratoRequest(BaseModel):
    texto: str
    nombre_archivo: str


# =====================================================================
# 🚀 ENDPOINT 1: PROCESAR CONTRATO (POST)
# =====================================================================
@app.post("/procesar-contrato/")
async def procesar_contrato(request: ContratoRequest):
    try:
        # Forzamos a que la ejecución pesada de la Crew corra en un hilo seguro y aislado.
        # Esto evita que FastAPI se congele o se bloquee mientras OpenAI responde.
        resultado = await asyncio.to_thread(ejecutar_analisis, request.texto)

        # Guardamos el resultado en la nube con Supabase de forma directa
        datos_insercion = {
            "nombre_archivo": request.nombre_archivo,
            "reporte_ia": resultado,
        }
        supabase.table(TABLA_HISTORIAL).insert(datos_insercion).execute()

        return {"resultado": resultado}
    except Exception as e:
        print(f"❌ Error en procesar_contrato: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# 📜 ENDPOINT 2: LEER HISTORIAL (GET)
# =====================================================================
@app.get("/historial/")
def leer_historial():
    try:
        # Traemos todos los registros desde Supabase ordenados por ID descendente
        respuesta = (
            supabase.table(TABLA_HISTORIAL).select("*").order("id", desc=True).execute()
        )
        registros = respuesta.data if hasattr(respuesta, "data") else []

        return {"total_analizados": len(registros), "registros": registros}
    except Exception as e:
        print(f"❌ Error en leer_historial: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# 🗑️ ENDPOINT 3: ELIMINAR CONTRATO (DELETE)
# =====================================================================
@app.delete("/eliminar-contrato/{contrato_id}")
def eliminar_contrato(contrato_id: int):
    try:
        # Eliminamos el registro de la tabla en Supabase usando el ID que manda el Frontend
        supabase.table(TABLA_HISTORIAL).delete().eq("id", contrato_id).execute()

        return {
            "status": "success",
            "message": f"Contrato {contrato_id} eliminado exitosamente de la base de datos.",
        }
    except Exception as e:
        print(f"❌ Error en eliminar_contrato: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Supabase Error: {str(e)}")
