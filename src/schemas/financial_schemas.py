from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
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
        populate_by_name = True
        arbitrary_types_allowed = True

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
    _id: str
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
    _id: str
    class Config:
        from_attributes = True


class MetaAhorroBase(BaseModel):
    usuario_id: str
    nombre: str
    monto_objetivo: float
    monto_actual: float
    fecha_inicio: datetime
    fecha_objetivo: datetime

    @field_validator('fecha_inicio', 'fecha_objetivo')
    def convert_date_to_datetime(cls, v):
        # Si v es una instancia de date, conviértelo a datetime con hora 00:00:00
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        return v


class MetaAhorroCreate(MetaAhorroBase):
    pass


class MetaAhorro(MongoBaseModel, MetaAhorroBase):
    _id: str
    class Config:
        from_attributes = True


class TransaccionBase(BaseModel):
    usuario_id: str
    monto: float
    fecha: datetime
    descripcion: str

    @field_validator('fecha')
    def convert_date_to_datetime(cls, v):
        # Si v es una instancia de date, conviértelo a datetime con hora 00:00:00
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        return v


class Transaccion(MongoBaseModel, TransaccionBase):
    _id: str
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
    fecha: datetime
    total_ingresos: float
    total_gastos: float
    balance: float

    @field_validator('fecha')
    def convert_date_to_datetime(cls, v):
        # Si v es una instancia de date, conviértelo a datetime con hora 00:00:00
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        return v


class ResumenMensual(MongoBaseModel, ResumenMensualBase):
    _id: str
    class Config:
        from_attributes = True