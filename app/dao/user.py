from .base import BaseDAO
from app.db.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import UUID


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def update_refresh_token(cls, session: AsyncSession, user_id: UUID, **data):
        """
        Обновляет поля пользователя. 
        Используется как для refresh_token, так и для профиля.
        """
        query = (
            update(cls.model)
            .where(cls.model.id == user_id)
            .values(**data)
        )
        await session.execute(query)
        await session.commit()
    
    @classmethod
    async def verify_and_update_refresh(cls, session: AsyncSession, user_id: UUID, new_token: str):
        user = await cls.find_one_or_none_by_id(session, id=user_id)

        if not user:
            return None
        
        user.refresh_token = new_token
        await session.commit()
        return user
    