from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    # Core envs
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Optional, comma-separated list for CORS
    FRONTEND_ORIGINS: str | None = None

    def database_url_async(self) -> str:
        """Return DATABASE_URL normalized for async psycopg.

        Accepts common inputs (postgres://, postgresql://, psycopg2) and
        coerces to postgresql+psycopg://. Appends sslmode=require for
        common managed providers when missing.
        """
        url = (self.DATABASE_URL or '').strip()
        # Normalize scheme to async psycopg (SQLAlchemy auto-selects async
        # when create_async_engine is used with +psycopg)
        if url.startswith('postgres://'):
            url = 'postgresql+psycopg://' + url[len('postgres://') :]
        elif url.startswith('postgresql://'):
            url = 'postgresql+psycopg://' + url[len('postgresql://') :]
        elif url.startswith('postgresql+psycopg2://'):
            url = 'postgresql+psycopg://' + url[len('postgresql+psycopg2://') :]

        # If pointing to DigitalOcean managed DB and sslmode missing, add it
        if 'ondigitalocean.com' in url and 'sslmode=' not in url:
            url += ('&' if '?' in url else '?') + 'sslmode=require'

        return url

    def cors_origins(self) -> list[str]:
        if not self.FRONTEND_ORIGINS:
            return []
        return [o.strip() for o in self.FRONTEND_ORIGINS.split(',') if o.strip()]
