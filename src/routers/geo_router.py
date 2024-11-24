from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.schemas.geo_schemas import EstadoGet, Pais, Estado
from src.controllers.geo_controller import obtener_estados, obtener_paises, obtener_estados_by_pais
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

@router.get("/paises/estados/{pais_id}", response_model=list[Estado])
def get_estados_by_pais(pais_id: int ,db: Session = Depends(get_db)):
    """
    Obtiene todos los estados con su país correspondiente en base al ID del país
    """
    return obtener_estados_by_pais(db, pais_id)

@router.get("/paises", response_model=list[Pais])
def get_paises(db: Session = Depends(get_db)):
    """
    Obtiene todos los países disponibles.
    """
    return obtener_paises(db)