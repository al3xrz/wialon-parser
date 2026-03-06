from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MAIN_URL: str
    LOGIN: str
    PASSWORD: str
    SLEEP_TIME: int
    SESSION_TIMEOUT: int

    class Config:
        env_file = ".env"


settings = Settings()
