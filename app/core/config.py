from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./wallets.db"
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test_wallets.db"

    class Config:
        env_file = ".env"


settings = Settings()
