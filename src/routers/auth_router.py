from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.schemas import auth_schemas
from src.controllers import auth_controller
from src.db.postgresql.config import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login", response_model=auth_schemas.Token)
def login(
    login_data: auth_schemas.Login,
    db: Session = Depends(get_db)
):
    return auth_controller.login(db, login_data.correo, login_data.contrasena)

@router.post("/register", response_model=auth_schemas.Token, status_code=201)
async def register(
    register_data: auth_schemas.Register,
    db: Session = Depends(get_db)
):
    return await auth_controller.register(db, register_data)
