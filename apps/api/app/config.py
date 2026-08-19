from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://groundeddesk:groundeddesk@localhost:5432/groundeddesk"
    jwt_secret: str = "change-me"
    jwt_ttl_minutes: int = 720
    cors_origins: str = "http://localhost:3000"
    ai_provider: str = "local"
    ai_force_failure: bool = False
    local_embedding_dimensions: int = 16
    worker_poll_seconds: float = 1.0

    @property
    def cors_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
