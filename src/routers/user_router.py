from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.schemas.user_schemas import UsuarioGet, UsuarioUpdate
from src.controllers import user_controller
from src.db.postgresql.config import get_db

from src.middlewares.auth_middleware import auth_middleware

router = APIRouter(
    prefix="/usuarios",
    tags=["Users"]
)

@router.get("/details", response_model=UsuarioGet, status_code=200, dependencies=[Depends(auth_middleware)])
async def obtener_detalles(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Obtener los detalles de un usuario
    """
    usuario_id = request.state.user.id
    usuario = await user_controller.obtener_detalles(db, usuario_id)
    return usuario

@router.put("/", response_model=dict, status_code=200, dependencies=[Depends(auth_middleware)])
async def actualizar_usuario(
    request: Request,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un usuario
    """
    usuario_id = request.state.user.id
    response = await user_controller.actualizar_usuario(db, usuario_id, usuario_data)
    return {"message": response["message"]}