from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


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
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
    )

    postgres_user: str = Field(env="POSTGRES_USER")
    postgres_password: SecretStr = Field(env="POSTGRES_PASSWORD")
    postgres_db: str = Field(env="POSTGRES_DB")
    postgres_host: str = Field(env="POSTGRES_HOST")
    postgres_port: int = Field(env="POSTGRES_PORT")

    jwt_secret_key: SecretStr = Field(env="JWT_SECRET_KEY")
    jwt_refresh_secret_key: SecretStr = Field(env="JWT_REFRESH_SECRET_KEY")
    jwt_algorithm: str = Field(validation_alias="ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")

    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

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
            algorithm=self.jwt_algorithm,
            access_token_expire_minutes=self.jwt_access_token_expire_minutes,
            refresh_token_expire_days=self.jwt_refresh_token_expire_days,
        )


@lru_cache
def get_settings() -> Config:
    return Config()


config = get_settings()
