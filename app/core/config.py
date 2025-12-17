from pydantic_settings import BaseSettings, SettingsConfigDict

"""Application configuration settings."""

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "project-reservation"
    env: str = "dev"

    db_host: str = "127.0.0.1"
    db_port: int = 5433
    db_name: str = "project-reservation"
    db_user: str = "postgres"
    db_password: str = "Itsbiggerthan1+"

settings = Settings()
