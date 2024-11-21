from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from bson import ObjectId


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
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoBaseModel(BaseModel):
    id: Optional[str] = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CategoriaGastoBase(BaseModel):
    """
    en usuario_id, va el UUID del usuario, o en caso de que el string de usuario_id 
    tenga el valor "default", aparecera para todos los usuarios de la plataforma
    """
    usuario_id: str
    nombre: str
    limite_gasto: float
    gasto_actual: float


class CategoriaGastoGet(MongoBaseModel, CategoriaGastoBase):
    total_gastado: float

    class Config:
        from_attributes = True


class CategoriaGastoCreate(CategoriaGastoBase):
    pass


class CategoriaGasto(MongoBaseModel, CategoriaGastoBase):
    class Config:
        from_attributes = True


class UsuarioFinancieroBase(BaseModel):
    usuario_id: str
    salario_mxn: Optional[float] = Field(None, description="Salario en MXN o null si no aplica")
    salario_usd: Optional[float] = Field(None, description="Salario en USD o null si no aplica")
    balance_objetivo: float
    gasto_limite: float


class UsuarioFinancieroCreate(UsuarioFinancieroBase):
    pass


class UsuarioFinanciero(MongoBaseModel, UsuarioFinancieroBase):
    class Config:
        from_attributes = True


class MetaAhorroBase(BaseModel):
    usuario_id: str
    nombre: str
    monto_objetivo: float
    monto_actual: float
    fecha_inicio: date
    fecha_objetivo: date


class MetaAhorroCreate(MetaAhorroBase):
    pass


class MetaAhorro(MongoBaseModel, MetaAhorroBase):
    class Config:
        from_attributes = True


class TransaccionBase(BaseModel):
    usuario_id: str
    monto: float
    fecha: date
    descripcion: str


class Transaccion(MongoBaseModel, TransaccionBase):
    class Config:
        from_attributes = True


class GastoCreate(TransaccionBase):
    categoria_id: str


class Gasto(Transaccion):
    categoria_id: str


class IngresoCreate(TransaccionBase):
    pass

class ResumenMensualBase(BaseModel):
    usuario_id: str
    fecha: date
    total_ingresos: float
    total_gastos: float
    balance: float


class ResumenMensual(MongoBaseModel, ResumenMensualBase):
    class Config:
        from_attributes = True