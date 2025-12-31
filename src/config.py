from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DATABASE_URL: str
    JWT_KEY: str
    JWT_ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Config()
