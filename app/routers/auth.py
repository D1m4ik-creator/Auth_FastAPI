from fastapi import status, HTTPException, APIRouter, Response, Depends, Request
from app.db.schemas.users import UserCreate, UserOut, User
from app.core.engine import SessionDep, get_session
from app.core.security import create_access_token, refresh_decode_token, create_refresh_token
from app.core.config import get_settings
from app.dao.user import UsersDAO
from app.db.schemas.users import UserLogin, Token
import app.crud.users as crud_user



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/create_user/", response_model=UserOut)
async def create_user(db: SessionDep, user_in: UserCreate):
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    return await crud_user.create(db, obj_in=user_in)

@router.post("/login_user/")
async def auth_user(db: SessionDep, user_data: UserLogin, response: Response):
    user = await crud_user.authenticate_user(db, email=user_data.email, password=user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token_lifetime_seconds = get_settings().jwt.access_token_expire_minutes * 60
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token_lifetime_days = get_settings().jwt.refresh_token_expire_days * 60 * 60 * 24
    refresh_token = create_refresh_token({"sub": str(user.id)})
    await UsersDAO.update_refresh_token(db, user_id=user.id, refresh_token=refresh_token)

    response.set_cookie(
        key="users_access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=access_token_lifetime_seconds,
        expires=access_token_lifetime_seconds,
    )
    response.set_cookie(
        key="users_refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=refresh_token_lifetime_days,
        expires=refresh_token_lifetime_days,
    )
    return {'message': 'Успешная авторизация'}


@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    response.delete_cookie(key="users_refresh_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.post("/refresh/")
async def refresh(db: SessionDep, request: Request, response: Response):
    old_refresh = request.cookies.get("users_refresh_token")
    user_id = refresh_decode_token(old_refresh).get("sub")

    new_access = create_access_token({"sub": str(user_id)})
    new_refresh = create_refresh_token({"sub": str(user_id)})

    user = await UsersDAO.verify_and_update_refresh(db, user_id=user_id, new_token=new_refresh)

    if not user:
        raise HTTPException(status_code=401, detail="Refresh failed")
    
    response.set_cookie(
        key="users_access_token", 
        value=new_access, 
        httponly=True,
        samesite="lax"
    )
    response.set_cookie(
        key="users_refresh_token",
        value=new_refresh,
        httponly=True,
        samesite="lax"
    )
    return {"status": "ok"}
