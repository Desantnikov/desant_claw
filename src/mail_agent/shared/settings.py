from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    INTERNAL_EMAIL_ADDRESS: str = Field()
    OPENAI_API_KEY: str = Field()
    DEFAULT_MODEL: str = Field()

    POSTGRES_DB: str = Field()
    POSTGRES_USER: str = Field()
    POSTGRES_PASSWORD: str = Field()
    DATABASE_URL: str = Field()

    # model_config = SettingsConfigDict(env_prefix='my_prefix_')


settings = Settings()
