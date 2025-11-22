import base64
import json
from typing import Any, Dict, Optional, List

from openai import OpenAI

from ..config import settings
from ..schemas.documents import (
    ExtractedDocument,
    DocumentType,
    CedulaData,
    ActaSeguroData,
    ContratoData,
)

# Cliente OpenAI
client = OpenAI(api_key=settings.openai_api_key)


SYSTEM_PROMPT = """
Eres un sistema experto en análisis de documentos legales y financieros en Colombia.
Tu tarea es:
1) Identificar el tipo de documento entre:
   - CEDULA
   - ACTA_SEGURO
   - CONTRATO
2) Extraer los campos estructurados definidos para ese tipo de documento.
3) Devolver SIEMPRE un único objeto JSON con la siguiente forma EXACTA:

{
  "doc_type": "CEDULA" | "ACTA_SEGURO" | "CONTRATO",
  "cedula": {
    "numero": string,
    "apellidos": string,
    "nombres": string,
    "fecha_nacimiento": string | null,
    "lugar_nacimiento": string | null,
    "estatura_m": number | null,
    "grupo_sanguineo_rh": string | null,
    "sexo": string | null,
    "fecha_expedicion": string | null,
    "lugar_expedicion": string | null
  } | null,
  "acta_seguro": {
    "compania": string | null,
    "nit_compania": string | null,
    "direccion_compania": string | null,
    "numero_poliza": string,
    "ramo": string | null,
    "tomador_asegurado": string | null,
    "identificacion": string | null,
    "fecha_emision": string | null,
    "ciudad_emision": string | null,
    "fecha_inicio": string | null,
    "fecha_fin": string | null,
    "coberturas": [
      { "nombre": string, "monto": string | null }
    ],
    "estado_poliza": string | null
  } | null,
  "contrato": {
    "numero_contrato": string | null,
    "contratante_nombre": string | null,
    "contratante_nit": string | null,
    "contratista_nombre": string | null,
    "contratista_identificacion": string | null,
    "objeto": string | null,
    "valor_numerico": number | null,
    "valor_textual": string | null,
    "fecha_inicio": string | null,
    "fecha_fin": string | null,
    "duracion_meses": integer | null,
    "ciudad_firma": string | null,
    "fecha_firma": string | null,
    "clausulas_relevantes": string | null
  } | null
}

Reglas importantes:
- Si el documento no es de un tipo, el campo correspondiente debe ser null.
- Para cada fecha, intenta devolverla en formato YYYY-MM-DD cuando la información lo permita.
- Para números de identificación o pólizas, devuélvelos como string.
- En cédulas, presta especial atención a los campos de estatura y grupo sanguíneo RH.
  Estos pueden aparecer como "ESTATURA: 1.65 M", "ESTATURA 1,65 M", "G.S. RH: O+" u otras variantes.
  Debes mapear:
    - estatura_m: número en metros (por ejemplo 1.65 si ves "1.65 M" o "1,65 M").
    - grupo_sanguineo_rh: texto tal como "O+", "A-", "B+", etc.
- No escribas nada fuera del JSON.
"""


def _build_content(raw_text: Optional[str], image_bytes: Optional[bytes]) -> List[Dict[str, Any]]:
    """
    Construye la lista de 'content' para el mensaje del usuario.
    Puede incluir texto, imagen o ambos.
    """
    content: List[Dict[str, Any]] = []

    user_instructions = (
        "Analiza el siguiente documento (texto e imagen si está disponible). "
        "Recuerda devolver SOLO un JSON válido siguiendo la estructura indicada."
    )

    # Instrucciones
    content.append({"type": "text", "text": user_instructions})

    # Texto extraído del PDF (si hay)
    if raw_text:
        content.append({"type": "text", "text": raw_text})

    # Imagen en base64 (si hay)
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": data_url,
                },
            }
        )

    return content


def _parse_model_json(content: str) -> Dict[str, Any]:
    """Parsea el JSON devuelto por el modelo. Si falla, lanza ValueError."""
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"No se pudo parsear la respuesta JSON del modelo: {exc}") from exc


def classify_and_extract(
    raw_text: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
) -> ExtractedDocument:
    """
    Envía el documento al modelo de OpenAI (texto, imagen o ambos),
    clasifica el tipo y extrae los campos estructurados.
    """
    if not raw_text and not image_bytes:
        raise ValueError("Se requiere al menos texto o imagen para analizar el documento.")

    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": SYSTEM_PROMPT}],
        },
        {
            "role": "user",
            "content": _build_content(raw_text, image_bytes),
        },
    ]

    try:
        completion = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        # Cualquier fallo de la API se expone como ValueError hacia arriba
        raise ValueError(f"Error al llamar a la API de OpenAI: {exc}") from exc

    content = completion.choices[0].message.content
    data = _parse_model_json(content)

    # doc_type
    try:
        doc_type = DocumentType(data["doc_type"])
    except Exception as exc:
        raise ValueError(f"doc_type inválido en la respuesta del modelo: {data.get('doc_type')}") from exc

    # Submodelos
    cedula_model: Optional[CedulaData] = None
    acta_model: Optional[ActaSeguroData] = None
    contrato_model: Optional[ContratoData] = None

    cedula_payload = data.get("cedula")
    acta_payload = data.get("acta_seguro")
    contrato_payload = data.get("contrato")

    if cedula_payload:
        cedula_model = CedulaData(**cedula_payload)
    if acta_payload:
        acta_model = ActaSeguroData(**acta_payload)
    if contrato_payload:
        contrato_model = ContratoData(**contrato_payload)

    extracted = ExtractedDocument(
        doc_type=doc_type,
        raw_text=raw_text or "",
        cedula=cedula_model,
        acta_seguro=acta_model,
        contrato=contrato_model,
        quality_score=0.0,  # se calcula luego en evaluate_quality
        issues=[],
    )

    return extracted
