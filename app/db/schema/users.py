from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr
import re


PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,64}$")


class UserCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="SecurePassword123!")


    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not PASSWORD_RE.match(value):
            raise ValueError("Пароль должен быть от 8 до 64 символов и содержать хотя бы одну заглавную букву, одну строчную букву, одну цифру и один специальный символ.")
        return value
    

class User(BaseModel):
    id: int
    name: str
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="SecurePassword123!")