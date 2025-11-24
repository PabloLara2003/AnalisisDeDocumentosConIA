import os
import json
from typing import Any, Dict, List

import requests
import streamlit as st

# URL base del backend: en Docker es http://backend:8000
BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
PROCESS_URL = f"{BACKEND_BASE_URL.rstrip('/')}/documents/process"
HISTORY_URL = f"{BACKEND_BASE_URL.rstrip('/')}/documents/history"


def call_backend(file) -> Dict[str, Any] | None:
    """Envía el archivo al backend FastAPI y devuelve el JSON de respuesta."""
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
    """Obtiene el historial de documentos procesados desde el backend."""
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
