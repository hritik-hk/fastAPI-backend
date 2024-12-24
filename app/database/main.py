from sqlmodel import create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.config import Config

async_engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL,
        echo=True,
    )
)


async def init_db():
    async with async_engine.begin() as conn:
        statement = text("SELECT 'hello';")
        result = await conn.execute(statement)
        print(result.all())


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with Session() as session:
        yield session
