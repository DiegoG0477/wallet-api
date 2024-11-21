from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.schemas.geo_schemas import EstadoGet, Pais
from src.controllers.geo_controller import obtener_estados, obtener_paises
from src.db.postgresql.config import get_db

router = APIRouter(
    prefix="/geo",
    tags=["Geo"]
)

@router.get("/estados", response_model=list[EstadoGet])
def get_estados(db: Session = Depends(get_db)):
    """
    Obtiene todos los estados con su país correspondiente.
    """
    return obtener_estados(db)

@router.get("/paises", response_model=list[Pais])
def get_paises(db: Session = Depends(get_db)):
    """
    Obtiene todos los países disponibles.
    """
    return obtener_paises(db)