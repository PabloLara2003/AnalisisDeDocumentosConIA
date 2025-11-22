import json

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .security.files import validate_uploaded_file
from .services.pdf_reader import extract_text_from_pdf
from .services.openai_client import classify_and_extract
from .services.validation import evaluate_quality
from .schemas.documents import ExtractedDocument
from .schemas.history import DocumentHistoryItem
from .db import Base, engine, SessionLocal
from .models import DocumentRecord


app = FastAPI(
    title="Document Intelligence Backend",
    version="0.6.0",
    description=(
        "API para clasificar documentos (cédula, acta de seguros, contrato), "
        "extraer campos clave usando OpenAI, evaluar calidad de datos y "
        "persistir resultados para consulta posterior."
    ),
)

# CORS abierto para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod: restringir dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Eventos de aplicación 

@app.on_event("startup")
def on_startup():
    """Crea las tablas si no existen."""
    Base.metadata.create_all(bind=engine)

# Endpoints

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/documents/process", response_model=ExtractedDocument)
async def process_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # Validar archivo
    file_bytes = await validate_uploaded_file(file)

    raw_text = None
    image_bytes = None

    # Lógica según tipo MIME
    if file.content_type == "application/pdf":
        pdf_data = extract_text_from_pdf(file_bytes)
        if pdf_data["has_text"]:
            raw_text = pdf_data["full_text"]
        else:
            raise HTTPException(
                status_code=400,
                detail=(
                    "El PDF no contiene texto embebido. En esta versión no se procesan "
                    "PDFs escaneados sin texto (solo PDFs digitales e imágenes)."
                ),
            )
    elif file.content_type in ("image/jpeg", "image/png"):
        image_bytes = file_bytes
    else:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no soportado. Use PDF, JPG o PNG.",
        )

    # Llamar a OpenAI
    try:
        extracted = classify_and_extract(raw_text=raw_text, image_bytes=image_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error al interpretar la respuesta del modelo: {exc}",
        ) from exc

    # Evaluación de calidad
    extracted_with_quality = evaluate_quality(extracted)

    # Persistir en BD
    record = DocumentRecord(
        filename=file.filename,
        doc_type=extracted_with_quality.doc_type.value,
        quality_score=extracted_with_quality.quality_score,
        payload_json=extracted_with_quality.model_dump_json(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Respuesta
    return extracted_with_quality


@app.get("/documents/history", response_model=list[DocumentHistoryItem])
def list_documents_history(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    Historial de documentos procesados más recientes.
    Incluye el JSON completo (`payload`) para poder reconstruir el panel.
    """
    if limit < 1 or limit > 100:
        limit = 20

    records = (
        db.query(DocumentRecord)
        .order_by(DocumentRecord.created_at.desc())
        .limit(limit)
        .all()
    )

    items: list[DocumentHistoryItem] = []

    for r in records:
        payload: dict
        try:
            payload = json.loads(r.payload_json) if r.payload_json else {}
        except json.JSONDecodeError:
            payload = {}

        items.append(
            DocumentHistoryItem(
                id=r.id,
                filename=r.filename,
                doc_type=r.doc_type,
                quality_score=r.quality_score,
                created_at=r.created_at,
                payload=payload,
            )
        )

    return items
