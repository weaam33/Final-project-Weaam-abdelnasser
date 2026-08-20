from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """App configuration, overridable via a .env file or environment variables."""

    MODEL_PATH: str = str(BASE_DIR / "models" / "house_price.pkl")
    LOCATIONS_PATH: str = str(BASE_DIR / "models" / "locations.json")
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
