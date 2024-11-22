from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import user_models
from src.schemas.auth_schemas import Register, Token
from src.services.jwt_service import create_token
from src.services.encrypt_service import verify_password, hash_password
from src.services.uuid_service import generate_uuid
from src.db.mongodb.config import mongo_connection
from datetime import date

def login(db: Session, email: str, password: str):
    user = db.query(user_models.Usuario).filter(user_models.Usuario.correo == email).first()

    if not user or not verify_password(password, user.contrasena):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

async def save_financial_data_to_mongo(usuario_id: str, register_data: Register):
    """
    Guarda los datos financieros de un usuario en MongoDB.
    :param usuario_id: UUID del usuario.
    :param register_data: Datos de registro que incluyen la información financiera.
    """
    financial_data = {
        "usuario_id": usuario_id,
        "salario_mxn": register_data.salario_mxn,
        "salario_usd": register_data.salario_usd,
        "balance_objetivo": register_data.balance_objetivo,
        "gasto_limite": register_data.gasto_limite,
    }

    db = mongo_connection.database
    await db["usuarios_financieros"].insert_one(financial_data)


async def register(db: Session, register_data: Register) -> Token:
    """
    Registra un usuario en PostgreSQL y guarda sus datos financieros en MongoDB.
    """
    if db.query(user_models.Usuario).filter(user_models.Usuario.correo == register_data.correo).first():
        raise HTTPException(status_code=400, detail="Correo ya existente")

    user_uuid = generate_uuid()

    new_user = user_models.Usuario(
        id=user_uuid,
        nombre=register_data.nombre,
        correo=register_data.correo,
        contrasena=hash_password(register_data.contrasena),
        fecha_registro=date.today(),
        apellido_paterno=register_data.apellido_paterno,
        apellido_materno=register_data.apellido_materno,
        pais_id=register_data.pais_id,
        estado_id=register_data.estado_id,
        direccion=register_data.direccion,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    await save_financial_data_to_mongo(user_uuid, register_data)

    token = create_token({"user_id": new_user.id})
    return Token(access_token=token, token_type="bearer")
