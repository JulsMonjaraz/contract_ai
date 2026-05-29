import asyncio  # 👈 Importamos la librería de asincronismo nativa
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agentes import ejecutar_analisis
import database  # 👈 Importamos tu archivo con su nombre original

# Inicializamos la base de datos local
database.init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContratoRequest(BaseModel):
    texto: str
    nombre_archivo: str


# Convertimos el endpoint en asíncrono usando 'async def'
@app.post("/procesar-contrato/")
async def procesar_contrato(request: ContratoRequest):
    try:
        # Forzamos a que la ejecución pesada de la Crew corra en un hilo seguro y aislado.
        # Esto evita que FastAPI se congele o se bloquee mientras OpenAI responde.
        resultado = await asyncio.to_thread(ejecutar_analisis, request.texto)

        # Guardamos el resultado en SQLite usando tu módulo 'database'
        database.guardar_analisis(request.nombre_archivo, resultado)

        return {"resultado": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/historial/")
def leer_historial():
    try:
        registros = database.obtener_historial()
        return {"total_analizados": len(registros), "registros": registros}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
