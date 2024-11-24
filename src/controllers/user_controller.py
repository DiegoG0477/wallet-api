from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException
from src.models import user_models
from src.models.financial_models import UsuarioFinancieroModel
from src.schemas.user_schemas import UsuarioGet, UsuarioUpdate
from typing import Dict
from src.db.mongodb.config import mongo_connection
from datetime import date

async def obtener_detalles(db: Session, usuario_id: str):
    user = db.query(user_models.Usuario).filter(user_models.Usuario.id == usuario_id).first()

    financial_db: AsyncIOMotorCollection = mongo_connection.database["usuarios_financieros"]
    financial_user = await financial_db.find_one({"usuario_id": usuario_id})

    if financial_user:
        financial_user.pop("_id", None)

    combined_data = {
            **user.__dict__,
            **(financial_user or {}),
    }

    combined_data.pop("_sa_instance_state", None)

    detailed_user = UsuarioGet(**combined_data)

    return detailed_user

def filter_data_for_model(data: Dict, model) -> Dict:
    """
    Filtra los campos en un diccionario para que coincidan con los campos del modelo Pydantic.
    """
    allowed_fields = set(model.__annotations__.keys())
    return {key: value for key, value in data.items() if key in allowed_fields}

def get_sql_model_columns(model) -> set:
    """
    Devuelve un conjunto con los nombres de las columnas del modelo SQLAlchemy.
    """
    return set(c.name for c in model.__table__.columns)

async def actualizar_usuario(db: Session, usuario_id: str, usuario_data: UsuarioUpdate):
    """
    Modificar los datos de un usuario (excepto contraseña y fecha de registro)
    """
    usuario_data_dict = usuario_data.model_dump()
    sql_columns = get_sql_model_columns(user_models.Usuario)
    sql_data = {key: value for key, value in usuario_data_dict.items() if key in sql_columns}

    user = db.query(user_models.Usuario).filter(user_models.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for key, value in sql_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    financial_db: AsyncIOMotorCollection = mongo_connection.database["usuarios_financieros"]
    financial_columns = set(UsuarioFinancieroModel.__annotations__.keys())
    financial_data = {key: value for key, value in usuario_data_dict.items() if key in financial_columns}

    financial_result = await financial_db.update_one(
        {"usuario_id": usuario_id},
        {"$set": financial_data}
    )

    if financial_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario financiero no encontrado")

    return {"message": "Usuario actualizado correctamente"}