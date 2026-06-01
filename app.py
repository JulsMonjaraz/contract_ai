import streamlit as st
import requests
import io
import pdfplumber
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# =====================================================================
# 🛠️ 1. CONFIGURACIÓN DE BRANDING EN LA PESTAÑA
# =====================================================================
st.set_page_config(
    page_title="ContraxAI - Intelligent Contract Auditing",
    page_icon="⚖️",
    layout="wide",
)

# =====================================================================
# 🎨 2. SISTEMA DE DISEÑO Y UI GLOBAL
# =====================================================================
st.markdown(
    """
    <style>
        button[kind="primary"] {
            background-color: #007BFF !important; 
            border-radius: 8px !important;
            border: none !important;
            padding: 12px 24px !important;
            font-size: 16px !important;
            transition: background-color 0.3s ease;
        }
        button[kind="primary"] p {
            color: white !important;
            font-weight: bold !important;
        }
        button[kind="primary"]:hover {
            background-color: #0056b3 !important; 
        }
        button[kind="primary"]:hover p {
            color: white !important;
        }
        .css-163ttbj {
            background-color: #F8F9FA !important;
        }
        
        /* 📜 CLASES PERSONALIZADAS PARA CONTENEDORES */
        .caja-verde-segura {
            background-color: #064E3B !important; 
            padding: 22px !important; 
            border-radius: 8px !important; 
            border: 1px solid #047857 !important; 
            margin-bottom: 20px !important;
        }
        .caja-verde-segura p, .caja-verde-segura li, .caja-verde-segura div, .caja-verde-segura span {
            color: #D1FAE5 !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
        }
        .caja-verde-segura code, .caja-verde-segura pre {
            background-color: #047857 !important;
            color: white !important;
            border: none !important;
        }

        .caja-azul-segura {
            background-color: #0A2540 !important; 
            padding: 20px !important; 
            border-radius: 8px !important; 
            border: 1px solid #007BFF !important; 
            margin-bottom: 20px !important;
        }
        .caja-azul-segura p, .caja-azul-segura li, .caja-azul-segura div, .caja-azul-segura span {
            color: #E0F2FE !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# =====================================================================
# 🧠 3. MOTOR DE GENERACIÓN DE PDF
# =====================================================================
def generar_pdf_estilizado(titulo_contrato, texto_reporte):
    if not texto_reporte:
        texto_reporte = "No hay información disponible para este reporte."

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    story = []
    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "DocTitle",
        parent=estilos["Heading1"],
        fontSize=24,
        leading=28,
        textColor=HexColor("#007BFF"),
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    estilo_subtitulo = ParagraphStyle(
        "DocSubTitle",
        parent=estilos["Heading2"],
        fontSize=13,
        leading=16,
        textColor=HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
    )
    estilo_cuerpo = ParagraphStyle(
        "DocBody",
        parent=estilos["Normal"],
        fontSize=11,
        leading=16,
        textColor=HexColor("#334155"),
        alignment=TA_JUSTIFY,
        spaceAfter=10,
    )

    story.append(Paragraph("<b>CONTRAXAI - EXECUTIVE LEGAL AUDIT</b>", estilo_titulo))
    story.append(Paragraph(f"Documento analizado: {titulo_contrato}", estilo_subtitulo))
    story.append(Spacer(1, 15))

    texto_limpio = (
        texto_reporte.replace("**", "")
        .replace('<div class="caja-verde-segura">', "")
        .replace('<div class="caja-azul-segura">', "")
        .replace("</div>", "")
    )
    parrafos = texto_limpio.split("\n")
    for parrafo in parrafos:
        if parrafo.strip():
            if parrafo.strip().startswith("-") or parrafo.strip().startswith("*"):
                story.append(
                    Paragraph(f"• {parrafo.strip()[1:].strip()}", estilo_cuerpo)
                )
            else:
                story.append(Paragraph(parrafo.strip(), estilo_cuerpo))

    doc.build(story)
    buffer.seek(0)
    return buffer


# =====================================================================
# 🎛 4. INTERFAZ VISUAL: CONTRAXAI DASHBOARD
# =====================================================================

if "reporte_seleccionado" not in st.session_state:
    st.session_state.reporte_seleccionado = None
if "nombre_seleccionado" not in st.session_state:
    st.session_state.nombre_seleccionado = None
if "id_seleccionado" not in st.session_state:
    st.session_state.id_seleccionado = None
if "vista_activa" not in st.session_state:
    st.session_state.vista_activa = "dashboard"

st.markdown("<h1 style='text-align: center;'>ContraxAI 🛡️</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #3E9DF3; font-weight: normal;'>Secure Multi-Agent Contract Auditing & <span style='color: #3E9DF3;'>GDPR Compliance</span></h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div style='text-align: center; margin-bottom: 20px; font-size: 16px;'>Identify professional risks and protect your international relocation.</div>",
    unsafe_allow_html=True,
)
st.write("---")

BASE_URL = "http://127.0.0.1:8000"

st.sidebar.header("📜 ContraxAI Vault")

try:
    respuesta_historial = requests.get(f"{BASE_URL}/historial/").json()
    total = respuesta_historial.get("total_analizados", 0)
    st.sidebar.metric(label="Total Audited Contracts", value=total)
    st.sidebar.write("---")

    for registro in respuesta_historial.get("registros", []):
        if st.sidebar.button(
            f"{registro['nombre_archivo']}",
            key=f"vault_btn_{registro['id']}",
            use_container_width=True,
        ):
            st.session_state.reporte_seleccionado = registro["reporte_ia"]
            st.session_state.nombre_seleccionado = registro["nombre_archivo"]
            st.session_state.id_seleccionado = registro["id"]
            st.session_state.vista_activa = "historial"
            st.rerun()
except Exception as e:
    st.sidebar.error("Unable to connect to the ContraxAI secure vault.")


if st.session_state.vista_activa == "historial":
    st.markdown(
        f"### 📋 ContraxAI Intelligence Report: {st.session_state.nombre_seleccionado}"
    )

    reporte_crudo = st.session_state.reporte_seleccionado or "No data available."

    # Renderizado directo del HTML generado de manera nativa por la Crew
    st.markdown(reporte_crudo, unsafe_allow_html=True)

    st.write("---")
    col_pdf, col_delete, col_back = st.columns(3)

    with col_pdf:
        nombre_archivo_pdf = (
            f"ContraxAI_Report_{st.session_state.nombre_seleccionado}.pdf"
        )
        try:
            pdf_ejecutivo = generar_pdf_estilizado(
                st.session_state.nombre_seleccionado,
                st.session_state.reporte_seleccionado,
            )
            st.download_button(
                label="📥 Download Executive PDF",
                data=pdf_ejecutivo,
                file_name=nombre_archivo_pdf,
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error compiling PDF")

    with col_delete:
        if st.button("🗑️ Delete from Vault", use_container_width=True):
            contrato_id_actual = st.session_state.get("id_seleccionado")
            if contrato_id_actual:
                with st.spinner("Deleting record from secure vault..."):
                    try:
                        res = requests.delete(
                            f"{BASE_URL}/eliminar-contrato/{contrato_id_actual}"
                        )
                        if res.status_code == 200:
                            st.success("Contract successfully purged.")
                            st.session_state.reporte_seleccionado = None
                            st.session_state.nombre_seleccionado = None
                            st.session_state.id_seleccionado = None
                            st.session_state.vista_activa = "dashboard"
                            st.rerun()
                        else:
                            st.error(
                                "Failed to delete the contract from the cloud database."
                            )
                    except Exception as e:
                        st.error("Communication error with the core backend.")
            else:
                st.error("Contract ID not tracked in the current session.")

    with col_back:
        if st.button("🔄 Audit Another Contract", use_container_width=True):
            st.session_state.reporte_seleccionado = None
            st.session_state.nombre_seleccionado = None
            st.session_state.id_seleccionado = None
            st.session_state.vista_activa = "dashboard"
            st.rerun()

else:
    archivo_subido = st.file_uploader(
        "Upload your contract in PDF format", type=["pdf"]
    )

    if archivo_subido is not None:
        st.info(f"🔒 Document successfully staged: {archivo_subido.name}")

        if st.button("🚀 Launch ContraxAI Audit", type="primary"):
            with st.spinner(
                "The multi-agent crew is analyzing the document structure..."
            ):
                try:
                    texto_extraido = ""
                    with pdfplumber.open(archivo_subido) as pdf:
                        for page in pdf.pages:
                            pag_texto = page.extract_text()
                            if pag_texto:
                                texto_extraido += pag_texto + "\n"

                    payload_json = {
                        "texto": texto_extraido,
                        "nombre_archivo": archivo_subido.name,
                    }

                    respuesta = requests.post(
                        f"{BASE_URL}/procesar-contrato/", json=payload_json
                    )

                    if respuesta.status_code == 200:
                        resultado = respuesta.json()
                        st.success("Analysis successfully completed.")

                        st.session_state.reporte_seleccionado = resultado.get(
                            "resultado", "Sin resultado"
                        )
                        st.session_state.nombre_seleccionado = archivo_subido.name
                        st.session_state.vista_activa = "dashboard"
                        st.rerun()
                    else:
                        st.error(f"Audit Core Error ({respuesta.status_code})")
                except Exception as e:
                    st.error(f"Failed to communicate with the core backend.")

st.write("")
st.markdown(
    "<div style='text-align: center; color: #64748B; font-size: 12px; margin-top:100px;'>ContraxAI 🛡️ © 2026</div>",
    unsafe_allow_html=True,
)
