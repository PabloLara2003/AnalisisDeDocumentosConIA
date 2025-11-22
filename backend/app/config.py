from pathlib import Path
from typing import Optional, List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # Tamaño máximo en MB
    max_file_size_mb: int = 20

    # Extensiones permitidas (se usan en security/files.py)
    # validate_uploaded_file usa ext con punto (ej: ".pdf")
    allowed_extensions: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]


    # Tipos MIME permitidos
    allowed_mime_types: List[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
    ]

    #Base de datos 
    database_url: Optional[str] = None  

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def sqlalchemy_database_uri(self) -> str:
        """
        Por defecto usa SQLite en ./data/documents.db
        """
        if self.database_url:
            return self.database_url

        # Ruta al root del proyecto: .../DaviviendaPruebaTecnica
        base_dir = Path(__file__).resolve().parents[2]
        db_path = base_dir / "data" / "documents.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"


settings = Settings()
