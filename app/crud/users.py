from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import status, HTTPException, Response, Depends
from app.db.models.users import User
from app.db.schemas.users import UserCreate
from app.core.security import get_password_hash, verify_password, decode_token, get_token, validate_token


async def get_current_user(token: str = Depends(get_token)):
    payload = decode_token(token)

    if not validate_token(payload):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя')

    user = await UsersDAO.find_one_or_none_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    return user


async def get_by_email(db: AsyncSession, email: str):
    return (await db.execute(select(User).filter(User.email == email))).scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


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
