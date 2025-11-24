from __future__ import annotations

from typing import Literal

import streamlit as st

ViewName = Literal["analyze", "history"]


def render_header(current_view: ViewName) -> ViewName:
    """
    Renderiza el encabezado superior con el título y los botones de navegación.
    Devuelve la vista activa (analyze | history).
    """
    analyze_clicked = False
    history_clicked = False

    with st.container():
        # Contenedor para aplicar estilos CSS personalizados
        st.markdown('<div class="dv-header-bar">', unsafe_allow_html=True)

        col_title, col_nav = st.columns([3, 2])

        with col_title:
            st.markdown(
                "<div class='dv-header-title'>"
                "Davivienda - Herramienta interna de análisis de documentos"
                "</div>",
                unsafe_allow_html=True,
            )

        with col_nav:
            st.markdown('<div class="dv-nav-buttons">', unsafe_allow_html=True)

            col_analyze, col_history = st.columns(2)

            with col_analyze:
                label = "Analizar documento"
                if current_view == "analyze":
                    label += " ·"
                analyze_clicked = st.button(label, key="nav_analyze")

            with col_history:
                label = "Historial de documentos"
                if current_view == "history":
                    label += " ·"
                history_clicked = st.button(label, key="nav_history")

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if analyze_clicked:
        return "analyze"
    if history_clicked:
        return "history"
    return current_view
