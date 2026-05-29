import sqlite3
from datetime import datetime

DB_NAME = "contraxai_vault.db"


def init_db():
    """Crea la base de datos y la tabla si no existen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_archivo TEXT,
            fecha_analisis TEXT,
            reporte_ia TEXT
        )
    """)
    conn.commit()
    conn.close()


def guardar_analisis(nombre_archivo: str, reporte_ia: str):
    """Guarda un nuevo reporte en la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO historial_contratos (nombre_archivo, fecha_analisis, reporte_ia) VALUES (?, ?, ?)",
        (nombre_archivo, fecha_actual, reporte_ia),
    )
    conn.commit()
    conn.close()


def obtener_historial():
    """Recupera todos los reportes guardados, del más reciente al más antiguo."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre_archivo, fecha_analisis, reporte_ia FROM historial_contratos ORDER BY id DESC"
    )
    filas = cursor.fetchall()
    conn.close()

    return [
        {
            "id": fila[0],
            "nombre_archivo": fila[1],
            "fecha_analisis": fila[2],
            "reporte_ia": fila[3],
        }
        for fila in filas
    ]
