from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.users import User
from app.db.schema.users import UserCreate
from app.core.security import get_password_hash

async def get_by_email(db: AsyncSession, email: str):
    return (await db.execute(select(User).filter(User.email == email))).scalar_one_or_none()

async def create(db: AsyncSession, obj_in: UserCreate):
    db_obj = User(
        name=obj_in.name,
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
