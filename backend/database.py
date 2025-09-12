from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from backend.settings import Settings

engine = create_async_engine(Settings().ASYNC_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():  # pragma: no cover
    async with async_session_maker() as session:
        yield session
