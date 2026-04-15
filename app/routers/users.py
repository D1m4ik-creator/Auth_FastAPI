from fastapi import APIRouter, Depends
from app.db.schemas.users import User
import app.crud.users as crud_user


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/", response_model=User)
async def current_user(current_user: User = Depends(crud_user.get_current_user)):
    return current_user