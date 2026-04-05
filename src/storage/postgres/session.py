from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.settings import settings


engine = create_async_engine(settings.sqlalchemy_database_url, echo=False)

SessionFactory = async_sessionmaker(  # TODO: terminate explicitly?
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)