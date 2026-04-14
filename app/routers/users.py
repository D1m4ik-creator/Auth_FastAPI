from fastapi import status, HTTPException, APIRouter
from app.db.schema.users import UserCreate, UserOut
from app.core.engine import SessionDep
import app.crud.users as crud_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut)
async def create_user(user_in: UserCreate, db: SessionDep):
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    return await crud_user.create(db, obj_in=user_in)
