from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import date


class DocumentType(str, Enum):
    CEDULA = "CEDULA"
    ACTA_SEGURO = "ACTA_SEGURO"
    CONTRATO = "CONTRATO"


# CEDULA DE CIUDADANÍA
class CedulaData(BaseModel):
    numero: str = Field(..., description="Número de cédula, ej: '1.098.765.432'")
    apellidos: str
    nombres: str
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = None
    estatura_m: Optional[float] = Field(
        None, description="Estatura en metros, ej: 1.65"
    )
    grupo_sanguineo_rh: Optional[str] = Field(None, description="Ej: 'O+'")
    sexo: Optional[str] = Field(None, description="M/F")
    fecha_expedicion: Optional[date] = None
    lugar_expedicion: Optional[str] = None

    @validator("numero")
    def numero_no_vacio(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("El número de cédula no puede ser vacío")
        return v.strip()


# ACTA DE SEGURO
class CoberturaItem(BaseModel):
    nombre: str
    monto: Optional[str] = Field(
        None, description="Texto tal como aparece, ej: '$2.000.000.000 COP'"
    )


class ActaSeguroData(BaseModel):
    compania: Optional[str] = Field(
        None, description="Ej: 'SEGUROS BOLÍVAR S.A.'"
    )
    nit_compania: Optional[str] = None
    direccion_compania: Optional[str] = None

    numero_poliza: str
    ramo: Optional[str] = None
    tomador_asegurado: Optional[str] = None
    identificacion: Optional[str] = None

    fecha_emision: Optional[date] = None
    ciudad_emision: Optional[str] = None

    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None

    coberturas: List[CoberturaItem] = Field(
        default_factory=list,
        description="Coberturas y montos listados en el certificado",
    )

    estado_poliza: Optional[str] = None

    @validator("numero_poliza")
    def numero_poliza_no_vacio(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("El número de póliza no puede ser vacío")
        return v.strip()


# Contrato
class ContratoData(BaseModel):
    numero_contrato: Optional[str] = Field(
        None, description="Ej: '045-2024'"
    )
    contratante_nombre: Optional[str] = None
    contratante_nit: Optional[str] = None
    contratista_nombre: Optional[str] = None
    contratista_identificacion: Optional[str] = None

    objeto: Optional[str] = Field(
        None,
        description="Texto de la cláusula de objeto",
    )

    valor_numerico: Optional[float] = Field(
        None, description="Valor numérico del contrato si se puede parsear"
    )
    valor_textual: Optional[str] = Field(
        None,
        description="Texto completo del valor, ej: 'QUINCE MILLONES ... ($15.000.000 COP)'",
    )

    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    duracion_meses: Optional[int] = None

    ciudad_firma: Optional[str] = None
    fecha_firma: Optional[date] = None

    clausulas_relevantes: Optional[str] = Field(
        None,
        description="Resumen de cláusulas importantes (confidencialidad, terminación, etc.)",
    )


class FieldIssue(BaseModel):
    field_name: str
    issue_type: str  # ej: "missing", "invalid_format"
    message: str


class ExtractedDocument(BaseModel):
    doc_type: DocumentType
    raw_text: str = Field(..., description="Texto base usado para la extracción")
    cedula: Optional[CedulaData] = None
    acta_seguro: Optional[ActaSeguroData] = None
    contrato: Optional[ContratoData] = None

    quality_score: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Score global de calidad de datos (0 a 1)",
    )
    issues: List[FieldIssue] = Field(
        default_factory=list,
        description="Listado de problemas de calidad de datos detectados",
    )
