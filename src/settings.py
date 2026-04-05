from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    INTERNAL_EMAIL_ADDRESS: str = Field()
    OPENAI_API_KEY: str = Field()
    DEFAULT_MODEL: str = Field()

    # POSTGRES
    POSTGRES_DB: str = Field()
    POSTGRES_USER: str = Field()
    POSTGRES_PASSWORD: str = Field()
    DATABASE_URL: str = Field()

    # QDRANT
    QDRANT_HOST: str = Field()
    QDRANT_REST_PORT: int = Field()
    QDRANT_GRPC_PORT: int = Field()
    QDRANT_PREFER_GRPC: bool = Field()
    QDRANT_CLIENT_TIMEOUT: int = Field()

    # to make it use psycopg3
    @property
    def sqlalchemy_database_url(self) -> str:
        return self.DATABASE_URL.replace("postgresql://","postgresql+psycopg://")


settings = Settings()
