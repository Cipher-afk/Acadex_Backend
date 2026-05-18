from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets

secrets.token_hex()


class Config(BaseSettings):
    DATABASE_URL: str
    JWT_KEY: str
    JWT_ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: str
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    DOMAIN_NAME:str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Config()
