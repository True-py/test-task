from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Travel Planner API"
    app_version: str = "1.0.0"
    environment: str = "local"
    debug: bool = True

    database_url: str = "sqlite:///./travel_planner.db"

    art_api_base_url: str = "https://api.example.com/api/..."
    art_api_timeout_seconds: int = 10
    cache_ttl_seconds: int = 600

    require_auth: bool = False
    api_username: str = "admin"
    api_password: str = "admin123"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()