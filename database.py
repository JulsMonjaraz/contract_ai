import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Intentar obtener la URL de Supabase. Si no existe, usa SQLite local por defecto.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./contraxai_vault.db"

# Configuración limpia del motor de base de datos
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# =====================================================================
# 📊 DEFINICIÓN DEL MODELO / TABLA
# =====================================================================
class ContratoRegistro(Base):
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String(255), index=True)
    reporte_ia = Column(Text)


# =====================================================================
# 🛠️ FUNCIONES QUE UTILIZA TU MAIN.PY
# =====================================================================


def init_db():
    """Crea las tablas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)


def guardar_analisis(nombre_archivo: str, resultado_ia: str):
    """Guarda un nuevo reporte de auditoría en la base de datos cloud."""
    db = SessionLocal()
    try:
        nuevo_registro = ContratoRegistro(
            nombre_archivo=nombre_archivo, reporte_ia=resultado_ia
        )
        db.add(nuevo_registro)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def obtener_historial():
    """Recupera todos los contratos auditados ordenados por ID desc."""
    db = SessionLocal()
    try:
        # Hacemos la consulta y transformamos los objetos en diccionarios para FastAPI
        filas = db.query(ContratoRegistro).order_by(ContratoRegistro.id.desc()).all()
        resultado = []
        for fila in filas:
            resultado.append(
                {
                    "id": fila.id,
                    "nombre_archivo": fila.nombre_archivo,
                    "reporte_ia": fila.reporte_ia,
                }
            )
        return resultado
    except Exception as e:
        raise e
    finally:
        db.close()
