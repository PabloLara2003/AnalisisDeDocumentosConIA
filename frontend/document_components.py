# frontend/document_components.py

from typing import Dict, Any, List

import pandas as pd
import streamlit as st

from backend_client import fetch_history


# =========================
#  BADGE DE CALIDAD
# =========================

def quality_badge(score: float) -> str:
    """Devuelve HTML de un pequeño badge según el quality_score."""
    if score >= 0.9:
        color = "#0A8754"  # verde
        label = "Alta"
    elif score >= 0.7:
        color = "#F2C14E"  # amarillo
        label = "Media"
    else:
        color = "#D64545"  # rojo
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


# =========================
#  TARJETAS KEY–VALUE
# =========================

def render_key_value_card(data: Dict[str, Any], field_labels: Dict[str, str]) -> None:
    """
    Muestra un diccionario de datos como tarjeta 2 columnas.
    """
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


# =========================
#  SECCIONES POR TIPO
# =========================

def render_cedula_section(cedula: Dict[str, Any]) -> None:
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


def render_acta_seguro_section(acta: Dict[str, Any]) -> None:
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
            <div style="margin-top:12px;font-size:13px;font-weight:600;">Coberturas</div>
            """,
            unsafe_allow_html=True,
        )
        df = pd.DataFrame(coberturas)
        df = df.rename(columns={"nombre": "Cobertura", "monto": "Monto"})
        st.table(df)


def render_contrato_section(contrato: Dict[str, Any]) -> None:
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


# =========================
#  RESULTADO DE UN DOCUMENTO
# =========================

def render_document_result(result: Dict[str, Any], filename: str) -> None:
    """
    Panel de resultado:
    - Cabecera: nombre, tipo, calidad.
    - Cuerpo: datos estructurados + observaciones.
    """
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

    # Datos estructurados
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

    # Observaciones de calidad
    with c2:
        st.markdown(
            "<div style='font-size:14px;font-weight:600;margin-bottom:8px;color:#383636;'>"
            "Observaciones de calidad</div>",
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


# =========================
#  VISTA: HISTORIAL
# =========================

def render_history_view() -> None:
    """Vista de historial de documentos procesados con filtro por tipo."""
    st.markdown(
        """
        <div style="margin-top:0;margin-bottom:8px;">
            <div style="font-size:20px;font-weight:600;color:#222222;margin-bottom:4px;">
                Historial de documentos
            </div>
            <div style="font-size:13px;color:#555555;max-width:900px;">
                Consulte los últimos documentos analizados, filtrando por tipo de documento
                (cédula, contrato o acta de seguro).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----- Filtro por tipo de documento -----
    tipo_opciones = ["Todos", "Cédula", "Contrato", "Seguro"]
    tipo_map = {
        "Todos": None,
        "Cédula": "CEDULA",
        "Contrato": "CONTRATO",
        "Seguro": "ACTA_SEGURO",
    }

    col_filtro, _ = st.columns([2, 3])
    with col_filtro:
        seleccion = st.selectbox(
            "Filtrar por tipo de documento",
            options=tipo_opciones,
            index=0,
        )

    tipo_filtrado = tipo_map[seleccion]

    # ----- Obtener historial desde el backend -----
    history = fetch_history(limit=50)
    if history is None:
        return

    # Filtrar por tipo (si aplica)
    filtered_history: List[Dict[str, Any]] = []
    for item in history:
        doc_type = item.get("doc_type", "—")
        if tipo_filtrado is not None and doc_type != tipo_filtrado:
            continue
        filtered_history.append(item)

    if len(filtered_history) == 0:
        st.info("No hay documentos en el historial para el filtro seleccionado.")
        return

    # ----- Render de cada item del historial -----
    for item in filtered_history:
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
