from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from .config import get_settings

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
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
