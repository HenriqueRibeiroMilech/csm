import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from backend.settings import Settings

_settings = Settings()
_db_url = _settings.database_url_async()

# Helpful log to confirm driver in deploys (masking credentials)
try:
    _masked = _db_url
    if '@' in _masked:
        creds, rest = _masked.split('@', 1)
        if '://' in creds:
            scheme, auth = creds.split('://', 1)
            _masked = f"{scheme}://***:***@{rest}"
    logging.getLogger(__name__).info("Using DATABASE_URL=%s", _masked)
except Exception:  # pragma: no cover - best-effort mask
    pass

engine = create_async_engine(_db_url, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():  # pragma: no cover
    async with async_session_maker() as session:
        yield session
