from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    REDIS_URL: str
    OPENAI_API_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
