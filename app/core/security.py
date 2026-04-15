from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import status, HTTPException, Request
from datetime import datetime, timedelta, timezone
from .config import get_settings

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Хэширует пароль с помощью passlib"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, что планируемый пароль соответствует хэшированному паролю"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Создание access токена"""
    to_encode = data.copy()
    jwt_settings = get_settings().jwt
    expire = datetime.now(timezone.utc) + timedelta(minutes=jwt_settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(
        to_encode,
        jwt_settings.secret_key.get_secret_value(),
        algorithm=jwt_settings.algorithm,
    )
    return encode_jwt


def create_refresh_token(data: dict) -> str:
    """Создание refresh токена"""
    to_encode = data.copy()
    jwt_settings = get_settings().jwt
    expire = datetime.now(timezone.utc) + timedelta(days=jwt_settings.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_settings.refresh_secret_key.get_secret_value(), algorithm=jwt_settings.algorithm)
    return encoded_jwt


def access_decode_token(token: str) -> dict:
    """Декодирует аксес токен и возвращает его полезную нагрузку, если токен не валидный, то вызывает HTTPException с кодом 401"""
    try:
        auth_data = get_settings().jwt
        return jwt.decode(token, auth_data.secret_key.get_secret_value(), algorithms=[auth_data.algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    

def refresh_decode_token(token: str) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token не найден",
        )

    jwt_settings = get_settings().jwt
    try:
        return jwt.decode(
            token,
            jwt_settings.refresh_secret_key.get_secret_value(),
            algorithms=[jwt_settings.algorithm],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token не валидный",
        )

def validate_token(payload: dict) -> bool:
    """Валидирует токен по полю exp, возвращает True если токен валидный, иначе False"""
    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        return False
    return True


def get_token(request: Request):
    """Получает токен из cookie с ключом 'users_access_token', если токен не найден, то вызывает HTTPException с кодом 401"""
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не найден')
    return token

