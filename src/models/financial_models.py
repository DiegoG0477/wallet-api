from bson import ObjectId
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, GetJsonSchemaHandler

class PyObjectId(ObjectId):
    """Soporte para convertir ObjectId entre Pydantic y MongoDB."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: dict, handler: GetJsonSchemaHandler):
        """Definir el esquema JSON para ObjectId."""
        schema.update(type="string")
        return schema


class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CategoriaGastoModel(MongoBaseModel):
    """
    Modelo de la colección `categorias_gasto`
    """
    usuario_id: str
    nombre: str
    limite_gasto: float
    gasto_actual: float


class UsuarioFinancieroModel(MongoBaseModel):
    """
    Modelo de la colección `usuarios_financieros`
    """
    usuario_id: str
    salario_mxn: Optional[float] = None
    salario_usd: Optional[float] = None
    balance_objetivo: float
    gasto_limite: float


class MetaAhorroModel(MongoBaseModel):
    """
    Modelo de la colección `metas_ahorro`
    """
    usuario_id: str
    nombre: str
    monto_objetivo: float
    monto_actual: float
    fecha_inicio: datetime
    fecha_objetivo: datetime


class TransaccionModel(MongoBaseModel):
    """
    Modelo base de la colección `transacciones`
    """
    usuario_id: str
    monto: float
    fecha: datetime
    descripcion: str


class GastoModel(TransaccionModel):
    """
    Modelo de la colección `gastos` (extiende transacciones)
    """
    categoria_id: str


class IngresoModel(TransaccionModel):
    """
    Modelo de la colección `ingresos` (extiende transacciones)
    """
    pass


class ResumenMensualModel(MongoBaseModel):
    """
    Modelo de la colección `resumen_mensual`
    """
    usuario_id: str
    fecha: datetime
    total_ingresos: float
    total_gastos: float
    balance: float
