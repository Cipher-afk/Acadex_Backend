from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DATABASE_URL: str
    JWT_KEY: str
    JWT_ALGORITHM: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Config()
