from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models.sqlDATA import Base


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///db.sql"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = async_sessionmaker(engine)


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
