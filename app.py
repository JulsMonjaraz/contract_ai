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
        
        /* 📜 CLASES PERSONALIZADAS PARA PREVENIR ERRORES DE FORMATO DE LA IA */
        /* 🟢 CONTENEDOR ANÁLISIS DE IMPACTO */
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

        /* 🔵 CONTENEDOR MARCO DE MITIGACIÓN */
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

    texto_limpio = texto_reporte.replace("**", "")
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
if "vista_activa" not in st.session_state:
    st.session_state.vista_activa = "dashboard"

st.markdown("<h1 style='text-align: center;'>ContraxAI 🛡️</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #3E9DF3; font-weight: normal;'>Secure Multi-Agent Contract Auditing & <span style='color: #3E9DF3;'>GDPR Compliance</span></h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div style='text-align: center; margin-bottom: 20px; font-size: 16px;'>"
    "Identify <span style='color: white;'>fraudulent clauses</span>, "
    "mitigate international relocation risks, and "
    "<span style='color: white;'>secure your professional future</span> overseas."
    "</div>",
    unsafe_allow_html=True,
)
st.write("---")

# URL Base Global de Producción en Render (Con barras diagonales correctas)
BASE_URL = "https://contract-ai-z10o.onrender.com"

# ---- CONEXIÓN DINÁMICA A LA BASE DE DATOS EN LA NUBE ----
st.sidebar.header("📜 ContraxAI Vault")

try:
    # Llamamos a /historial/ con la barra al final tal como está en tu main.py
    respuesta_historial = requests.get(f"{BASE_URL}/historial/").json()

    # Extraemos los datos usando las llaves exactas de tu main.py
    total = respuesta_historial.get("total_analizados", 0)
    st.sidebar.metric(label="Total Audited Contracts", value=total)
    st.sidebar.write("---")

    for registro in respuesta_historial.get("registros", []):
        if st.sidebar.button(
            f"{registro['nombre_archivo']}",
            key=f"vault_btn_{registro['id']}",
            use_container_width=True,
        ):
            # Tu base de datos guarda la columna como 'reporte_ia'
            st.session_state.reporte_seleccionado = registro["reporte_ia"]
            st.session_state.nombre_seleccionado = registro["nombre_archivo"]
            st.session_state.vista_activa = "historial"
            st.rerun()
except Exception as e:
    st.sidebar.error("Unable to connect to the ContraxAI secure vault.")


# =====================================================================
# 🔀 CONTROL DE VISTAS (PANTALLAS)
# =====================================================================

if st.session_state.vista_activa == "historial":
    # ---- PANTALLA A: DETALLE DEL REPORTE SELECCIONADO ----
    st.markdown(
        f"""
        <div style='background-color: #1E293B; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-left: 5px solid #10B981;'>
            <h3 style='margin: 0; color: white;'>📋 ContraxAI Intelligence Report</h3>
            <p style='margin: 5px 0 0 0; color: #94A3B8; font-size: 14px;'>Target Document: <b>{st.session_state.nombre_seleccionado}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    reporte_crudo = (
        st.session_state.reporte_seleccionado or "No auditing data available."
    )
    reporte_texto = reporte_crudo.replace("**", "")

    impacto_bloque = "No specific visa impact data found."
    mitigacion_bloque = ""

    marcador = "plan de mitigación:"
    texto_minusculas = reporte_texto.lower()

    if marcador in texto_minusculas:
        indice_corte = texto_minusculas.index(marcador)
        impacto_bloque = (
            reporte_texto[:indice_corte]
            .replace("Impacto en el Visado:", "")
            .replace("IMPACTO EN EL VISADO:", "")
            .strip()
        )
        mitigacion_bloque = (
            reporte_texto[indice_corte:]
            .replace("Plan de Mitigación:", "")
            .replace("Plan de mitigación:", "")
            .replace("PLAN DE MITIGACIÓN:", "")
            .strip()
        )
    else:
        marcador_plan_b = "mitigación"
        if marcador_plan_b in texto_minusculas:
            indice_corte = texto_minusculas.index(marcador_plan_b)
            impacto_bloque = (
                reporte_texto[:indice_corte]
                .replace("Impacto en el Visado:", "")
                .strip()
            )
            mitigacion_bloque = reporte_texto[indice_corte:].strip()
        else:
            impacto_bloque = reporte_texto.replace("Impacto en el Visado:", "").strip()

    st.markdown("### 🚨 Visa & Relocation Impact Analysis")
    impacto_html_formateado = impacto_bloque.replace("\n", "<br>")

    html_caja_verde = f"""
<div class="caja-verde-segura">
<div style="border-bottom: 1px solid #059669; padding-bottom: 10px; margin-bottom: 15px;">
<h4 style="margin: 0; color: #F0FDF4; font-size: 17px;">📋 LEGAL RISK SUMMARY & AUDIT DISCLOSURE</h4>
<p style="margin: 3px 0 0 0; color: #A7F3D0; font-size: 12px; text-transform: uppercase;">Status: Review Completed | Severity Tier: Critical Contingency Check</p>
</div>
<p style="margin-bottom: 12px;"><b>1. EXECUTIVE ANALYSIS & COMPLIANCE WARNING:</b><br>
This section details the primary risk variables extracted by the multi-agent legal engine. Any discrepancy identified below could jeopardize cross-border verification, temporary residency status, or immediate professional relocation compliance due to hidden enforcement metrics.</p>
<p style="margin-bottom: 15px;"><b>2. CORE VULNERABILITY FINDINGS:</b><br>{impacto_html_formateado}</p>
<div style="background-color: #047857; padding: 12px; border-radius: 6px; border-left: 4px solid #34D399; margin-top: 10px;">
<span style="font-size: 13px; color: #F0FDF4; display: block;">⚠️ <b>Relocation Advisory Note:</b> If the text above identifies unvouched terminations or strict jurisdictional bindings, legal oversight recommends halting automated execution until a physical framework amendment is staged.</span>
</div>
</div>
"""

    with st.container():
        st.markdown(html_caja_verde, unsafe_allow_html=True)

    if mitigacion_bloque:
        st.markdown("### 🛠️ Strategic Mitigation Framework")
        with st.expander("📋 Deployment Plan & Continuous Monitoring", expanded=True):
            with st.container():
                st.markdown(
                    f'<div class="caja-azul-segura">{mitigacion_bloque}</div>',
                    unsafe_allow_html=True,
                )

    st.write("---")
    col_pdf, col_back = st.columns(2)

    with col_pdf:
        nombre_limpio = (
            str(st.session_state.nombre_seleccionado).replace(".pdf", "")
            if st.session_state.nombre_seleccionado
            else "Report"
        )
        nombre_archivo_pdf = f"ContraxAI_Report_{nombre_limpio}.pdf"
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
            st.error(f"Error compiling PDF: {str(e)}")

    with col_back:
        if st.button(
            "🔄 Audit Another Contract", type="secondary", use_container_width=True
        ):
            st.session_state.reporte_seleccionado = None
            st.session_state.nombre_seleccionado = None
            st.session_state.vista_activa = "dashboard"
            st.rerun()

else:
    # ---- PANTALLA B: FILE UPLOADER PRINCIPAL ----
    archivo_subido = st.file_uploader(
        "Upload your contract in PDF format for encrypted analysis", type=["pdf"]
    )

    if archivo_subido is not None:
        st.info(f"🔒 Document successfully staged for analysis: {archivo_subido.name}")

        if st.button("🚀 Launch ContraxAI Audit", type="primary"):
            with st.spinner(
                "The multi-agent crew is analyzing the document structure..."
            ):
                try:
                    # Extraemos el texto localmente en Streamlit usando pdfplumber
                    texto_extraido = ""
                    with pdfplumber.open(archivo_subido) as pdf:
                        for page in pdf.pages:
                            pag_texto = page.extract_text()
                            if pag_texto:
                                texto_extraido += pag_texto + "\n"

                    # 🛠️ ENVÍO EN FORMATO JSON EXACTO (ContratoRequest)
                    payload_json = {
                        "texto": texto_extraido,
                        "nombre_archivo": archivo_subido.name,
                    }

                    # Apuntamos a /procesar-contrato/ con barra final como tu main.py
                    respuesta = requests.post(
                        f"{BASE_URL}/procesar-contrato/", json=payload_json
                    )

                    if respuesta.status_code == 200:
                        resultado = respuesta.json()
                        st.success("Analysis successfully completed.")

                        # Tu main.py devuelve {"resultado": resultado}
                        st.session_state.reporte_seleccionado = resultado.get(
                            "resultado", "Sin resultado"
                        )
                        st.session_state.nombre_seleccionado = archivo_subido.name
                        st.session_state.vista_activa = "historial"
                        st.rerun()
                    else:
                        st.error(
                            f"Audit Core Error ({respuesta.status_code}): {respuesta.text}"
                        )
                except Exception as e:
                    st.error(
                        f"Failed to communicate with the ContraxAI backend core: {str(e)}"
                    )

    else:
        st.write("")
        st.info(
            "💡 Please upload a new contract above or select an existing record from the ContraxAI Vault sidebar to view an active audit."
        )

# =====================================================================
# ⚡ 5. FOOTER GLOBAL FIJO
# =====================================================================
st.write("")
st.write("")
html_footer = """
<div style="text-align: center; margin-top: 180px; padding: 15px; border-top: 1px solid #1E293B;">
<p style="color: #64748B; font-size: 15px; margin: 0;">
    ContraxAI 🛡️ © 2026 | Encrypted Multi-Agent Core Framework | All Rights Reserved.
</p>
<p style="color: #475569; font-size: 11px; margin: 4px 0 0 0;">
    Designed for secure international relocation analytics and automated GDPR clause validation.
</p>
</div>
"""
st.markdown(html_footer, unsafe_allow_html=True)
