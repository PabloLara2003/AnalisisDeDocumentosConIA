from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class DocumentHistoryItem(BaseModel):
    id: int
    filename: str
    doc_type: str
    quality_score: float
    created_at: datetime
    payload: Dict[str, Any]
