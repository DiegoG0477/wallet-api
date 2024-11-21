from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from src.models.user_models import Estado, Pais
from src.schemas.geo_schemas import Pais as PaisSchema, EstadoGet

def obtener_estados(db: Session) -> list[EstadoGet]:
    """
    Obtiene todos los estados con su país correspondiente.
    """
    query = (
        db.query(
            Estado.id,
            Estado.nombre,
            Pais.nombre.label("pais")
        )
        .join(Pais, Estado.pais_id == Pais.id)
        .order_by(Estado.nombre)
    )
    estados = query.all()

    return [EstadoGet(id=estado.id, nombre=estado.nombre, pais=estado.pais) for estado in estados]


def obtener_paises(db: Session) -> list[PaisSchema]:
    """
    Obtiene todos los países disponibles.
    """
    query = db.query(Pais).order_by(Pais.nombre)
    paises = query.all()

    return [PaisSchema(id=pais.id, nombre=pais.nombre) for pais in paises]