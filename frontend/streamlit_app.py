import os
from typing import Any, Dict

import streamlit as st

from backend_client import call_backend
from document_components import render_document_result
from history_view import render_history_view
from header import render_header
from styles import inject_global_css

# URL base del backend: en Docker es http://backend:8000
BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
PROCESS_URL = f"{BACKEND_BASE_URL.rstrip('/')}/documents/process"


def get_current_view() -> str:
    """
    Determina la vista actual a partir del query param ?view=.
    Si no viene nada o viene algo raro, usa 'analyze'.
    """
    params = st.query_params
    view = params.get("view", "analyze")
    if isinstance(view, (list, tuple)):
        view = view[0] if view else "analyze"
    if view not in ("analyze", "history"):
        view = "analyze"
    return view


def main() -> None:
    st.set_page_config(
        page_title="Davivienda - Análisis de documentos",
        layout="wide",
    )

    # CSS global
    inject_global_css()

    # Estado para recordar el último documento procesado
    if "last_result" not in st.session_state:
        st.session_state["last_result"] = None
        st.session_state["last_filename"] = None

    # Vista actual inicial (desde el query param)
    current_view = get_current_view()

    # Topbar roja con título + navegación (puede actualizar la vista)
    current_view = render_header(current_view)

    # Sincronizar el query param con la vista actual
    st.query_params["view"] = current_view

    # ==== VISTA: ANALIZAR DOCUMENTO ====
    if current_view == "analyze":
        st.markdown(
            """
            <div class="dv-content">
                <div class="dv-section-title">
                    Análisis automatizado de documentos
                </div>
                <div class="dv-section-subtitle">
                    Cargue documentos de identificación, actas de seguro o contratos.
                    El sistema clasificará el tipo de documento, extraerá los campos principales
                    y evaluará la consistencia de la información para apoyar la revisión operativa.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_left, _ = st.columns([2, 3])

        with col_left:
            st.markdown(
                '<div class="dv-content">'
                '<div class="dv-uploader-title">Carga de documentos</div>',
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
                <div class="dv-uploader-help">
                    Se permiten archivos PDF, JPG y PNG. El procesamiento se realiza de forma interna
                    y los documentos no se exponen a interfaces públicas.
                </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        result_to_show: Dict[str, Any] | None = None
        filename_to_show: str | None = None

        if uploaded_file is not None:
            # Si es el mismo archivo, usamos el resultado cacheado
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
            # Si no hay archivo cargado pero ya hubo uno antes, lo mostramos
            if st.session_state.get("last_result") is not None:
                result_to_show = st.session_state["last_result"]
                filename_to_show = st.session_state.get("last_filename", "Documento")

        if result_to_show:
            with st.container():
                st.markdown('<div class="dv-content">', unsafe_allow_html=True)
                render_document_result(result_to_show, filename=filename_to_show or "Documento")
                st.markdown("</div>", unsafe_allow_html=True)

    # ==== VISTA: HISTORIAL ====
    else:
        st.markdown('<div class="dv-content">', unsafe_allow_html=True)
        render_history_view()
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
