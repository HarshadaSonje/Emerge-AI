from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    CLOUD_SQL_CONNECTION_NAME: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)

        # Cloud Run + Cloud SQL
        if self.CLOUD_SQL_CONNECTION_NAME:
            return (
                f"postgresql://{self.POSTGRES_USER}:"
                f"{encoded_password}@/"
                f"{self.POSTGRES_DB}"
                f"?host=/cloudsql/{self.CLOUD_SQL_CONNECTION_NAME}"
            )

        # Local development
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{encoded_password}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings()
