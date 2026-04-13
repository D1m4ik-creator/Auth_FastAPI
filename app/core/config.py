from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    user: str
    password: SecretStr
    db: str
    host: str
    port: int
    echo: bool = False

    def get_db_url(self) -> str:
        encoded_password = quote_plus(self.password.get_secret_value())
        return f"postgresql+asyncpg://{self.user}:{encoded_password}@{self.host}:{self.port}/{self.db}"


class JWTConfig(BaseModel):
    secret_key: SecretStr
    refresh_secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: SecretStr = Field(alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: int = Field(alias="POSTGRES_PORT")

    jwt_secret_key: SecretStr = Field(alias="JWT_SECRET_KEY")
    jwt_refresh_secret_key: SecretStr = Field(alias="JWT_REFRESH_SECRET_KEY")

    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    @property
    def database(self) -> DatabaseConfig:
        return DatabaseConfig(
            user=self.postgres_user,
            password=self.postgres_password,
            db=self.postgres_db,
            host=self.postgres_host,
            port=self.postgres_port,
            echo=self.database_echo,
        )

    @property
    def jwt(self) -> JWTConfig:
        return JWTConfig(
            secret_key=self.jwt_secret_key,
            refresh_secret_key=self.jwt_refresh_secret_key,
        )


@lru_cache
def get_settings() -> Config:
    return Config()


config = get_settings()
