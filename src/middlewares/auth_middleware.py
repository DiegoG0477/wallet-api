from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session
from src.db.postgresql.config import get_db
from src.models.user_models import Usuario
from src.services.jwt_service import verify_token

async def auth_middleware(
    request: Request,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if "user_id" not in token:
        raise HTTPException(status_code=401, detail="Token de usuario inválido")
    
    user = db.query(user).filter(user.id == token["user_id"]).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    request.state.user = user
    return user
