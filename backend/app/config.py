from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_NAME: str

    class Config:
        env_file = ".env"

settings = Settings() 