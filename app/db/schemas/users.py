import uuid
import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,64}$")


class User(BaseModel):
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not PASSWORD_RE.match(value):
            raise ValueError("Пароль должен быть от 8 до 64 символов и содержать хотя бы одну заглавную букву, одну строчную букву, одну цифру и один специальный символ.")
        return value
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr


class Token(BaseModel):
    token: str
