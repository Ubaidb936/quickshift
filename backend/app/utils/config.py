from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "changeme-in-production"
    DATABASE_URL: str = "postgresql://quickshift:quickshift@db:5432/quickshift"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
