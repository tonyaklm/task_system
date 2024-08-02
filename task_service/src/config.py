from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://{}:{}@postgresql:5432/{}".format(
        os.getenv("POSTGRES_USER"), os.getenv("POSTGRES_PASSWORD"), os.getenv("POSTGRES_DB"))
    algorithm: str = "HS256"
    jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY")


settings = Settings()
