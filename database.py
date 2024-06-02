
from datetime import date
import os
from typing import Optional, AsyncGenerator

from asyncpg.exceptions import (
    ConnectionDoesNotExistError,
    ConnectionFailureError
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.expression import func

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class DB_Error(Exception):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with new_session() as session:
            yield session
    except ConnectionDoesNotExistError or ConnectionFailureError as e:
        raise DB_Error(e)


class Model(DeclarativeBase):
    def __repr__(self) -> str:
        cols = [f'{col} = {getattr(self, col)}'
                for col in self.__table__.columns.keys()]
        return f'<{self.__class__.__name__}: {", ".join(cols)}>'

    # У нас только одна модель, но repr лучше сразу
    # прописать здесь для масштабируемости


class MetalRoll(Model):
    __tablename__ = 'metalrolls'
    id: Mapped[int] = mapped_column(primary_key=True)
    length: Mapped[int]
    weight: Mapped[int]
    loaded_at: Mapped[date] = mapped_column(
        server_default=func.current_date()
    )
    unloaded_at: Mapped[Optional[date]]

    # В задании требуется именно дата, хотя для склада
    # мне кажется лучше полный таймстэмп (current_timestamp)
