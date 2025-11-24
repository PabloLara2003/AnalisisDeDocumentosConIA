from typing import Any, Dict, List, Optional

import streamlit as st

from backend_client import fetch_history
from document_components import render_document_result


def render_history_view() -> None:
    """Vista de historial de documentos procesados con filtro por tipo."""
    st.markdown(
        """
        <div class="dv-content">
            <div class="dv-section-title">Historial de documentos</div>
            <div class="dv-section-subtitle">
                Consulte los últimos documentos analizados, filtrando por tipo de documento
                (cédula, contrato o acta de seguro).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----- Filtro por tipo de documento (selectbox estilo dropdown) -----
    st.markdown(
        '<div class="dv-content" style="padding-top:12px;">',
        unsafe_allow_html=True,
    )

    tipo_opciones = ["Todos", "Cédula", "Contrato", "Seguro"]
    tipo_map = {
        "Todos": None,
        "Cédula": "CEDULA",
        "Contrato": "CONTRATO",
        "Seguro": "ACTA_SEGURO",
    }

    col_filtro, _ = st.columns([2, 3])
    with col_filtro:
        st.markdown('<div class="dv-filter-select">', unsafe_allow_html=True)
        seleccion = st.selectbox(
            "Filtrar por tipo de documento",
            options=tipo_opciones,
            index=0,
            key="history_filter",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    tipo_filtrado: Optional[str] = tipo_map[seleccion]

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

    st.markdown(
        '<div class="dv-content" style="padding-top:12px;">',
        unsafe_allow_html=True,
    )

    if len(filtered_history) == 0:
        st.info("No hay documentos en el historial para el filtro seleccionado.")
        st.markdown("</div>", unsafe_allow_html=True)
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

    st.markdown("</div>", unsafe_allow_html=True)
