import re
from datetime import date
from typing import List

from ..schemas.documents import (
    ExtractedDocument,
    FieldIssue,
    DocumentType,
)


def _add_issue(
    issues: List[FieldIssue],
    field_name: str,
    issue_type: str,
    message: str,
):
    issues.append(
        FieldIssue(
            field_name=field_name,
            issue_type=issue_type,
            message=message,
        )
    )


def _enrich_cedula_from_text(extracted: ExtractedDocument) -> None:
    """
    Intenta completar estatura_m y grupo_sanguineo_rh a partir del raw_text si vienen vacíos.
    """
    if extracted.doc_type != DocumentType.CEDULA or not extracted.cedula:
        return

    c = extracted.cedula
    text = (extracted.raw_text or "").upper()

    # Estatura: patrones tipo "ESTATURA: 1.65 M" o "ESTATURA 1,65 M"
    if c.estatura_m is None:
        m = re.search(r"ESTATURA\s*[:\-]?\s*([0-9]+(?:[.,][0-9]+)?)\s*M", text)
        if m:
            value_str = m.group(1).replace(",", ".")
            try:
                c.estatura_m = float(value_str)
            except ValueError:
                pass

    # Grupo sanguíneo RH: patrones tipo "G.S. RH: O+"
    if not c.grupo_sanguineo_rh:
        m = re.search(r"G\.?\s*S\.?\s*RH\s*[:\-]?\s*([ABO0][+-])", text)
        if m:
            group = m.group(1)
            # Algunas veces la O puede aparecer como 0
            group = group.replace("0", "O")
            c.grupo_sanguineo_rh = group


def evaluate_quality(extracted: ExtractedDocument) -> ExtractedDocument:
    """
    Aplica reglas de validación de datos sobre el documento extraído
    y calcula un quality_score entre 0 y 1.
    Además, en el caso de cédula intenta enriquecer estatura y RH a partir del texto.
    """
    # Enriquecer cédula con regex antes de evaluar
    _enrich_cedula_from_text(extracted)

    issues: List[FieldIssue] = []
    checks_total = 0
    checks_ok = 0

    def check(condition: bool, field_name: str, issue_type: str, message: str):
        nonlocal checks_total, checks_ok
        checks_total += 1
        if condition:
            checks_ok += 1
        else:
            _add_issue(issues, field_name, issue_type, message)

    today = date.today()

    # Validaciones por tipo de documento
    if extracted.doc_type == DocumentType.CEDULA and extracted.cedula:
        c = extracted.cedula

        # Número de cédula no vacío
        check(
            bool(c.numero and c.numero.strip()),
            "cedula.numero",
            "missing",
            "Número de cédula vacío o ausente.",
        )

        # Fecha de nacimiento no en el futuro
        if c.fecha_nacimiento:
            check(
                c.fecha_nacimiento <= today,
                "cedula.fecha_nacimiento",
                "invalid_format",
                "Fecha de nacimiento en el futuro.",
            )

        # Fecha de expedición no en el futuro
        if c.fecha_expedicion:
            check(
                c.fecha_expedicion <= today,
                "cedula.fecha_expedicion",
                "invalid_format",
                "Fecha de expedición en el futuro.",
            )

        # Estatura y grupo sanguíneo presentes si están en la cédula
        check(
            c.estatura_m is not None,
            "cedula.estatura_m",
            "missing",
            "No se detectó la estatura en la cédula.",
        )

        check(
            bool(c.grupo_sanguineo_rh),
            "cedula.grupo_sanguineo_rh",
            "missing",
            "No se detectó el grupo sanguíneo RH en la cédula.",
        )

    if extracted.doc_type == DocumentType.ACTA_SEGURO and extracted.acta_seguro:
        a = extracted.acta_seguro

        # Número de póliza obligatorio
        check(
            bool(a.numero_poliza and a.numero_poliza.strip()),
            "acta_seguro.numero_poliza",
            "missing",
            "Número de póliza vacío o ausente.",
        )

        # Rango de fechas coherente
        if a.fecha_inicio and a.fecha_fin:
            check(
                a.fecha_inicio <= a.fecha_fin,
                "acta_seguro.fecha_rango",
                "invalid_format",
                "Fecha de inicio posterior a la fecha de fin.",
            )

        # Fecha de emisión no en el futuro
        if a.fecha_emision:
            check(
                a.fecha_emision <= today,
                "acta_seguro.fecha_emision",
                "invalid_format",
                "Fecha de emisión en el futuro.",
            )

    if extracted.doc_type == DocumentType.CONTRATO and extracted.contrato:
        c = extracted.contrato

        # Si hay fechas de inicio y fin, que el rango tenga sentido
        if c.fecha_inicio and c.fecha_fin:
            check(
                c.fecha_inicio <= c.fecha_fin,
                "contrato.fecha_rango",
                "invalid_format",
                "Fecha de inicio posterior a la fecha de fin.",
            )

        # Valor numérico > 0 si existe
        if c.valor_numerico is not None:
            check(
                c.valor_numerico > 0,
                "contrato.valor_numerico",
                "invalid_format",
                "Valor del contrato debe ser mayor que 0.",
            )

    # Calculo de quality_score 
    if checks_total > 0:
        quality_score = checks_ok / checks_total
    else:
        quality_score = 0.0

    # Devolvemos un nuevo modelo con los campos actualizados
    updated = ExtractedDocument(
        **extracted.model_dump(exclude={"quality_score", "issues"}),
        quality_score=quality_score,
        issues=issues,
    )
    return updated
