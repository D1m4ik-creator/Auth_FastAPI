from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None
    
    @classmethod
    async def find_all(cls, session: AsyncSession):
        query = select(cls.model)
        result = await session.execute(query)
        return result.scalars().all()
        
    @classmethod
    async def find_one_or_none_by_id(cls, session: AsyncSession, **kwargs):
        """Нахождение пользователя по id"""
        query = select(cls.model).filter_by(**kwargs)
        result = await session.execute(query)
        return result.scalars().one_or_none()
    
