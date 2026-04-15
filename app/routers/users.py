from fastapi import status, HTTPException, APIRouter
from app.db.schema.users import UserCreate, UserOut
from app.core.engine import SessionDep
from app.core.security import create_access_token
from app.core.config import get_settings
from app.db.schema.users import UserLogin
from fastapi import Response
import app.crud.users as crud_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut)
async def create_user(user_in: UserCreate, db: SessionDep):
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    return await crud_user.create(db, obj_in=user_in)

@router.post("/login/")
async def auth_user(db: SessionDep, user_data: UserLogin, response: Response):
    user = await crud_user.authenticate_user(db, email=user_data.email, password=user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token_lifetime_seconds = get_settings().jwt.access_token_expire_minutes * 60
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="users_access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=access_token_lifetime_seconds,
        expires=access_token_lifetime_seconds,
    )
    return {'message': 'Успешная авторизация'}
