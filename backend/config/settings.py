"""
Application Settings & Configuration
Centralized configuration for the Financial Risk & Collections Assistant.
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:
    """Application-wide settings."""

    # --- Application ---
    APP_NAME: str = "AI Financial Risk & Collections Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list = field(default_factory=lambda: [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ])

    # --- Paths ---
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = field(init=False)
    UPLOAD_DIR: Path = field(init=False)
    REPORTS_DIR: Path = field(init=False)
    MODELS_DIR: Path = field(init=False)
    CHARTS_DIR: Path = field(init=False)
    DB_PATH: Path = field(init=False)

    # --- Database ---
    DATABASE_URL: str = field(init=False)

    # --- AI / OpenAI ---
    OPENAI_API_KEY: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    OPENAI_MODEL: str = "gpt-4o-mini"

    # --- ML ---
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    CV_FOLDS: int = 5

    # --- Security ---
    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", "dev-secret-key-change-in-production"
        )
    )

    def __post_init__(self):
        self.DATA_DIR = self.BASE_DIR / "data"
        self.UPLOAD_DIR = self.DATA_DIR / "uploads"
        self.REPORTS_DIR = self.DATA_DIR / "reports"
        self.MODELS_DIR = self.DATA_DIR / "models"
        self.CHARTS_DIR = self.DATA_DIR / "charts"
        self.DB_PATH = self.DATA_DIR / "app.db"
        self.DATABASE_URL = f"sqlite:///{self.DB_PATH}"

        # Create directories
        for d in [
            self.DATA_DIR,
            self.UPLOAD_DIR,
            self.REPORTS_DIR,
            self.MODELS_DIR,
            self.CHARTS_DIR,
        ]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
