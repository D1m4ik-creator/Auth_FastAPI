from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import status, HTTPException, Response, Depends
from app.db.models.users import User
from app.db.schemas.users import UserCreate
from app.core.security import get_password_hash, verify_password, access_decode_token, get_token
from app.core.engine import SessionDep
from app.dao.user import UsersDAO

async def get_current_user(db: SessionDep, token: str = Depends(get_token)):
    payload = access_decode_token(token)

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя')

    user = await UsersDAO.find_one_or_none_by_id(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь не найден')

    return user


async def get_by_email(db: SessionDep, email: str):
    return (await db.execute(select(User).filter(User.email == email))).scalar_one_or_none()


async def authenticate_user(db: SessionDep, email: str, password: str) -> User | None:
    user = await get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create(db: SessionDep, obj_in: UserCreate):
    db_obj = User(
        name=obj_in.name,
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
