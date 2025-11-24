import streamlit as st


def inject_global_css() -> None:
    """
    Estilos globales de la app:
    - Layout sin margenes raros
    - Header con título rojo subrayado y botones rojos
    - Paleta: blanco / gris claro / rojo Davivienda
    """
    st.markdown(
        """
        <style>
        /* =============================
           RESET Y CONTENEDORES BÁSICOS
           ============================= */

        html, body {
            margin: 0;
            padding: 0;
        }

        .stApp {
            background-color: #F5F5F5;
        }

        div[data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }

        div[data-testid="stAppViewContainer"] > .main {
            padding-top: 0 !important;
            padding-left: 0.1 !important;
            padding-right: 0.1 !important;
        }

        div[data-testid="block-container"] {
            padding-top: 0 !important;
            padding-bottom: 2rem;
            padding-left: 0 !important;
            padding-right: 0 !important;
            max-width: 100% !important;
        }

        /* Algunos layouts de Streamlit meten padding extra */
        div.st-emotion-cache-zy6yx3 {
            padding: 0 !important;
        }

        /* Ocultar barra superior y sidebar nativos de Streamlit */
        div[data-testid="stToolbar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }

        /* =============================
           HEADER PERSONALIZADO
           ============================= */

        .dv-header-bar {
            width: 100%;
            background-color: #FFFFFF;
            box-sizing: border-box;
            padding: 12px 48px 10px 48px;
            border-bottom: 1px solid #E0E0E0;
        }

        .dv-header-title {
            font-size: 24px;
            font-weight: 700;
            color: #B00020;              /* Rojo principal */
            text-decoration: underline;  /* Título subrayado */
        }

        .dv-nav-buttons {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            background-color: #8C0018 !important;
        }

        /* Botones de navegación: ROJOS con texto blanco */
        .dv-nav-buttons .stButton > button {
            background-color: #B00020 !important;
            color: #FFFFFF !important;
            border-radius: 999px !important;
            border: 1px solid #8C0018 !important;
            padding: 0.25rem 1.25rem !important;
            font-size: 13px !important;
            font-weight: 600 !important;
        }

        .dv-nav-buttons .stButton > button:hover {
            background-color: #8C0018 !important;
            border-color: #8C0018 !important;
        }

        .dv-nav-buttons .stButton {
            margin-left: 6px;
            margin-right: 6px;
            background-color: #8C0018 !important;
        }

        /* =============================
           CONTENIDO PRINCIPAL
           ============================= */

        .dv-content {
            padding: 16px 48px 0 48px;
        }

        .dv-section-title {
            font-size: 22px;
            font-weight: 600;
            color: #B00020;   /* títulos en rojo */
            margin-bottom: 4px;
        }

        .dv-section-subtitle {
            font-size: 13px;
            color: #555555;
            max-width: 900px;
        }

        .dv-uploader-title {
            font-size: 14px;
            font-weight: 600;
            margin: 12px 0 6px 0;
            color: #B00020;
        }

        .dv-uploader-help {
            font-size: 11px;
            color: #777777;
            margin-top: 4px;
            max-width: 600px;
        }

        /* =============================
           KEY-VALUE CARDS
           ============================= */

        .kv-card {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            column-gap: 24px;
        }

        .kv-row {
            margin-bottom: 6px;
        }

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

        /* Nombre del archivo debajo del uploader */
        div[data-testid="stFileUploader"] > div:nth-child(2) span {
            color: #222222 !important;
        }

        /* =============================
           EXPANDERS (historial, resultados)
           ============================= */

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
            background-color: #ECEFF1 !important;  /* evitar barra negra */
        }

        /* Texto interno siempre legible */
        div[data-testid="stExpander"] p,
        div[data-testid="stExpander"] span,
        div[data-testid="stExpander"] div,
        div[data-testid="stExpander"] table,
        div[data-testid="stExpander"] th,
        div[data-testid="stExpander"] td {
            color: #222222;
        }

        /* =============================
           SELECTBOX DEL FILTRO (HISTORIAL)
           ============================= */

        .dv-filter-select {
            font-size: 13px;
        }

        /* Contenedor del select: bordes y fondo claros */
        .dv-filter-select div[data-baseweb="select"] > div {
            border-radius: 8px !important;
            border-color: #B00020 !important;
            background-color: #FFFFFF !important;
            min-height: 36px;
        }

        .dv-filter-select div[data-baseweb="select"] > div:hover {
            border-color: #8C0018 !important;
        }

        .dv-filter-select span {
            font-size: 14px;
            color: #222222;
        }

        /* Hacer que el select NO sea editable:
           ocultamos el input de texto (solo queda el label y el caret). */
        .dv-filter-select input {
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
