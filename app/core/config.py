"""Settings loaded from environment. See .env.example."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kb_path: str = "data/kb"
    chroma_path: str = ".chroma"
    db_url: str = "sqlite:///./app.sqlite3"

    # Regions not on this list trigger refusal. Never infer from a neighbouring region.
    region_allowlist: list[str] = ["tainan"]

    # Slices older than this get a staleness warning attached to their citation.
    kb_stale_days: int = 365


settings = Settings()
