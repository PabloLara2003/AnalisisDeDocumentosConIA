import os
import json
from typing import List, Dict, Any

import pandas as pd
import requests
import streamlit as st

BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
PROCESS_URL = f"{BACKEND_BASE_URL.rstrip('/')}/documents/process"
HISTORY_URL = f"{BACKEND_BASE_URL.rstrip('/')}/documents/history"


def call_backend(file) -> Dict[str, Any] | None:
    files = {
        "file": (file.name, file.getvalue(), file.type),
    }

    try:
        response = requests.post(PROCESS_URL, files=files, timeout=60)
    except requests.RequestException as e:
        st.error(f"Error al conectar con el backend: {e}")
        return None

    if response.status_code != 200:
        st.error(f"Error del backend ({response.status_code}): {response.text}")
        return None

    try:
        return response.json()
    except json.JSONDecodeError:
        st.error("La respuesta del backend no es JSON válido.")
        return None


def fetch_history(limit: int = 20) -> List[Dict[str, Any]] | None:
    try:
        response = requests.get(HISTORY_URL, params={"limit": limit}, timeout=30)
    except requests.RequestException as e:
        st.error(f"Error al conectar con el backend (historial): {e}")
        return None

    if response.status_code != 200:
        st.error(
            f"Error del backend al obtener historial "
            f"({response.status_code}): {response.text}"
        )
        return None

    try:
        return response.json()
    except json.JSONDecodeError:
        st.error("La respuesta del backend (historial) no es JSON válido.")
        return None


def quality_badge(score: float) -> str:
    if score >= 0.9:
        color = "#0A8754"
        label = "Alta"
    elif score >= 0.7:
        color = "#F2C14E"
        label = "Media"
    else:
        color = "#D64545"
        label = "Baja"

    return f"""
    <span style="
        background-color:{color};
        color:white;
        padding:2px 8px;
        border-radius:12px;
        font-size:11px;
        font-weight:500;
        ">
        Calidad {label} ({score:.2f})
    </span>
    """


def render_key_value_card(data: dict, field_labels: dict):
    rows_html = ""
    for key, label in field_labels.items():
        value = data.get(key)
        if value is None or str(value).strip() == "":
            value_display = "<span style='color:#999999;'>—</span>"
        else:
            value_display = str(value)

        rows_html += f"""
        <div class="kv-row">
            <div class="kv-label">{label}</div>
            <div class="kv-value">{value_display}</div>
        </div>
        """

    st.markdown(
        f"""
        <div class="kv-card">
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cedula_section(cedula: dict):
    labels = {
        "numero": "Número de cédula",
        "apellidos": "Apellidos",
        "nombres": "Nombres",
        "fecha_nacimiento": "Fecha de nacimiento",
        "lugar_nacimiento": "Lugar de nacimiento",
        "estatura_m": "Estatura (m)",
        "grupo_sanguineo_rh": "Grupo sanguíneo RH",
        "sexo": "Sexo",
        "fecha_expedicion": "Fecha de expedición",
        "lugar_expedicion": "Lugar de expedición",
    }
    render_key_value_card(cedula, labels)


def render_acta_seguro_section(acta: dict):
    labels = {
        "compania": "Compañía",
        "nit_compania": "NIT compañía",
        "direccion_compania": "Dirección compañía",
        "numero_poliza": "Número de póliza",
        "ramo": "Ramo",
        "tomador_asegurado": "Tomador / Asegurado",
        "identificacion": "Identificación",
        "fecha_emision": "Fecha de emisión",
        "ciudad_emision": "Ciudad de emisión",
        "fecha_inicio": "Fecha inicio vigencia",
        "fecha_fin": "Fecha fin vigencia",
        "estado_poliza": "Estado de la póliza",
    }
    render_key_value_card(acta, labels)

    coberturas = acta.get("coberturas") or []
    if coberturas:
        st.markdown(
            """
            <div style="margin-top:1px;font-size:13px;font-weight:600;">Coberturas</div>
            """,
            unsafe_allow_html=True,
        )
        df = pd.DataFrame(coberturas)
        df = df.rename(columns={"nombre": "Cobertura", "monto": "Monto"})
        st.table(df)


def render_contrato_section(contrato: dict):
    labels_main = {
        "numero_contrato": "Número de contrato",
        "contratante_nombre": "Contratante",
        "contratante_nit": "NIT contratante",
        "contratista_nombre": "Contratista",
        "contratista_identificacion": "Identificación contratista",
        "fecha_inicio": "Fecha inicio",
        "fecha_fin": "Fecha fin",
        "duracion_meses": "Duración (meses)",
        "ciudad_firma": "Ciudad de firma",
        "fecha_firma": "Fecha de firma",
        "valor_numerico": "Valor numérico",
        "valor_textual": "Valor en letras",
    }
    render_key_value_card(contrato, labels_main)

    objeto = contrato.get("objeto")
    clausulas = contrato.get("clausulas_relevantes")

    if objeto:
        st.markdown(
            """
            <div style="margin-top:12px;font-size:13px;font-weight:600;">Objeto del contrato</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size:12px;color:#333333;margin-top:2px;'>{objeto}</div>",
            unsafe_allow_html=True,
        )

    if clausulas:
        st.markdown(
            """
            <div style="margin-top:12px;font-size:13px;font-weight:600;">Cláusulas relevantes</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size:12px;color:#333333;margin-top:2px;'>{clausulas}</div>",
            unsafe_allow_html=True,
        )


def render_document_result(result: dict, filename: str):
    doc_type = result.get("doc_type")
    quality_score = float(result.get("quality_score", 0.0))
    cedula = result.get("cedula")
    acta_seguro = result.get("acta_seguro")
    contrato = result.get("contrato")
    issues = result.get("issues", [])

    st.markdown(
        """
        <div style="
            border:1px solid #E0E0E0;
            border-radius:8px;
            padding:16px 20px;
            margin-top:8px;
            margin-bottom:16px;
            background-color:#FFFFFF;
        ">
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([3, 2, 3])

    with col1:
        st.markdown(
            f"""
            <div style="font-size:14px;color:#555555;">Documento</div>
            <div style="font-size:16px;font-weight:600;color:#222222;">{filename}</div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="font-size:14px;color:#555555;">Tipo detectado</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="font-size:16px;font-weight:600;color:#B00020;">
                {doc_type}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div style="font-size:14px;color:#555555;">Calidad de datos</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(quality_badge(quality_score), unsafe_allow_html=True)

    st.markdown("<hr style='margin:12px 0 16px 0;'>", unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown(
            "<div style='font-size:14px;font-weight:600;margin-bottom:8px;'>Datos extraídos</div>",
            unsafe_allow_html=True,
        )

        if doc_type == "CEDULA" and cedula:
            render_cedula_section(cedula)
        elif doc_type == "ACTA_SEGURO" and acta_seguro:
            render_acta_seguro_section(acta_seguro)
        elif doc_type == "CONTRATO" and contrato:
            render_contrato_section(contrato)
        else:
            st.write("No se encontraron datos estructurados para este documento.")

    with c2:
        st.markdown(
            "<div style='font-size:14px;font-weight:600;margin-bottom:8px;color:#383636;'>Observaciones de calidad</div>",
            unsafe_allow_html=True,
        )

        if issues:
            for issue in issues:
                field_name = issue.get("field_name")
                issue_type = issue.get("issue_type")
                message = issue.get("message")
                st.markdown(
                    f"""
                    <div style="
                        border:1px solid #F2D7D5;
                        background-color:#FDF2F2;
                        border-radius:6px;
                        padding:6px 8px;
                        margin-bottom:6px;
                        font-size:12px;
                    ">
                        <div style="font-weight:600;color:#A63A3A;">{field_name}</div>
                        <div style="color:#555555;">{message}</div>
                        <div style="color:#777777;font-size:11px;">Tipo: {issue_type}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div style="font-size:12px;color:#383636;">
                    No se registran observaciones de calidad para este documento.
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)


def render_history_view():
    st.markdown(
        """
        <div style="margin-top:8px;margin-bottom:8px;">
            <div style="font-size:20px;font-weight:600;color:#222222;margin-bottom:4px;">
                Historial de documentos
            </div>
            <div style="font-size:13px;color:#383636;max-width:900px;">
                Consulte los últimos documentos analizados, con su tipo detectado,
                la fecha de procesamiento y el puntaje de calidad de datos asociado.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = fetch_history(limit=20)
    if history is None:
        return

    if len(history) == 0:
        st.info("Todavía no hay documentos en el historial.")
        return

    for item in history:
        filename = item.get("filename", "—")
        doc_type = item.get("doc_type", "—")
        quality_score = float(item.get("quality_score", 0.0))
        created_at = item.get("created_at", "")
        payload = item.get("payload") or {}

        created_display = created_at.replace("T", " ")[:19] if created_at else "—"
        header = f"{filename} · {doc_type} · {created_display}"

        with st.expander(header, expanded=False):
            if "doc_type" not in payload:
                payload["doc_type"] = doc_type
            if "quality_score" not in payload:
                payload["quality_score"] = quality_score

            render_document_result(payload, filename=filename)


def inject_global_css():
    st.markdown(
        """
        <style>
        html, body {
            margin: 0;
            padding: 0;
        }

        .stApp {
            background-color: #F7F7F7;
            padding: 0 !important;
        }

        div[data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }

        div[data-testid="stAppViewContainer"] > .main {
            padding-top: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        div[data-testid="block-container"] {
            padding-top: 0 !important;
            padding-bottom: 2rem;
            padding-left: 0 !important;
            padding-right: 0 !important;
            max-width: 100% !important;
        }

        div[data-testid="block-container"] > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        div[data-testid="stToolbar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }

        .kv-card {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            column-gap: 24px;
        }

        .kv-row { margin-bottom: 6px; }

        .kv-label {
            font-size: 11px;
            font-weight: 600;
            color: #777777;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        .kv-value {
            font-size: 13px;
            color: #222222;
        }

        div[data-testid="stFileUploader"] > div:nth-child(2) span {
            color: #222222 !important;
        }

        button[kind="secondary"] {
            background-color: #B00020;
            color: #FFFFFF;
            border-radius: 20px;
            border: none;
            padding: 4px 16px;
            font-size: 13px;
        }

        button[kind="secondary"]:hover {
            background-color: #8C0018;
            color: #FFFFFF;
        }

        /* Estilos para los expansores del historial */
        div[data-testid="stExpander"] {
            margin-bottom: 8px;
        }

        div[data-testid="stExpander"] > details {
            background-color: #ECEFF1;
            border-radius: 8px;
            border: 1px solid #D0D4D8;
        }

        div[data-testid="stExpander"] > details > summary {
            padding: 6px 10px;
            font-weight: 600;
            color: #333333;
        }

        /* Forzar color de texto legible dentro de los expansores
           (Observaciones de calidad, Coberturas, etc.) */
        div[data-testid="stExpander"] p,
        div[data-testid="stExpander"] span,
        div[data-testid="stExpander"] div {
            color: #222222;
        }

        div[data-testid="stExpander"] table,
        div[data-testid="stExpander"] th,
        div[data-testid="stExpander"] td {
            color: #222222;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    with st.container():
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown(
                """
                <div style="padding: 0 32px 4px 32px;">
                    <div style="font-size:25px;font-weight:800;color:#B00020;">
                        Davivienda · Herramienta interna de análisis de documentos
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_right:
            view = st.session_state.get("view", "analyze")
            label_analyze = "Analizar documento" + ("" if view == "analyze" else "")
            label_history = "Historial de documentos" + (" ·" if view == "history" else "")

            c1, c2 = st.columns([1.2, 1.5])
            with c1:
                if st.button(label_analyze, key="nav_analyze"):
                    st.session_state["view"] = "analyze"
            with c2:
                if st.button(label_history, key="nav_history"):
                    st.session_state["view"] = "history"


def main():
    st.set_page_config(
        page_title="Davivienda - Análisis de documentos",
        layout="wide",
    )

    inject_global_css()

    if "view" not in st.session_state:
        st.session_state["view"] = "analyze"
    if "last_result" not in st.session_state:
        st.session_state["last_result"] = None
        st.session_state["last_filename"] = None

    render_header()
    current_view = st.session_state["view"]

    if current_view == "analyze":
        st.markdown(
            """
            <div style="padding: 4px 32px 0 32px;">
                <div style="font-size:22px;font-weight:600;color:#222222;margin-bottom:4px;">
                    Análisis automatizado de documentos
                </div>
                <div style="font-size:13px;color:#555555;max-width:900px;">
                    Cargue documentos de identificación, actas de seguro o contratos.
                    El sistema clasificará el tipo de documento, extraerá los campos principales
                    y evaluará la consistencia de la información para apoyar la revisión operativa.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='margin:8px 32px 0 32px;'>", unsafe_allow_html=True)

        col_left, _ = st.columns([2, 3])

        with col_left:
            st.markdown(
                "<div style='font-size:14px;font-weight:600;margin:12px 32px 6px 32px;color:#B00020;'>Carga de documentos</div>",
                unsafe_allow_html=True,
            )
            uploaded_file = st.file_uploader(
                "Seleccione un archivo en formato PDF o imagen",
                type=["pdf", "png", "jpg", "jpeg"],
                accept_multiple_files=False,
                label_visibility="collapsed",
            )

            st.markdown(
                """
                <div style="font-size:11px;color:#777777;margin:4px 32px 0 32px;">
                    Se permiten archivos PDF, JPG y PNG. El procesamiento se realiza de forma interna
                    y los documentos no se exponen a interfaces públicas.
                </div>
                """,
                unsafe_allow_html=True,
            )

        result_to_show = None
        filename_to_show = None

        if uploaded_file is not None:
            if (
                st.session_state.get("last_filename") == uploaded_file.name
                and st.session_state.get("last_result") is not None
            ):
                result_to_show = st.session_state["last_result"]
                filename_to_show = st.session_state["last_filename"]
            else:
                with st.spinner(f"Procesando {uploaded_file.name}..."):
                    result = call_backend(uploaded_file)

                if result:
                    st.session_state["last_result"] = result
                    st.session_state["last_filename"] = uploaded_file.name
                    result_to_show = result
                    filename_to_show = uploaded_file.name
        else:
            if st.session_state.get("last_result") is not None:
                result_to_show = st.session_state["last_result"]
                filename_to_show = st.session_state.get("last_filename", "Documento")

        if result_to_show:
            with st.container():
                st.markdown("<div style='padding:0 32px;'>", unsafe_allow_html=True)
                render_document_result(result_to_show, filename=filename_to_show)
                st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("<div style='padding: 4px 32px 0 32px;'>", unsafe_allow_html=True)
        render_history_view()
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
