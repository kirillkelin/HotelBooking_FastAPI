from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_async_engine(settings.database_url) #создаем асинхронный движок для передачи URL

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) #создение сессии

class Base(DeclarativeBase):
    pass
