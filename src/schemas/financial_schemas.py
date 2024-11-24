from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, Literal
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
    gasto_total: float

class CategoriaGastoCreate(CategoriaGastoBase):
    usuario_id: None = Field(default=None, exclude=True)
    gasto_total: None = Field(default=None, exclude=True)

class CategoriaGasto(MongoBaseModel, CategoriaGastoBase):
    _id: str
    deleted: int
    class Config:
        from_attributes = True

class CategoriaGastoGet(MongoBaseModel, CategoriaGastoBase):
    _id: str
    gasto_actual: float
    
    usuario_id: str = Field(exclude=True)
    deleted: int = Field(exclude=True)

class UsuarioFinancieroBase(BaseModel):
    usuario_id: str
    salario: float
    divisa: Literal["MXN", "USD"]
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
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        return v

class MetaAhorroCreate(MetaAhorroBase):
    usuario_id: None = Field(default=None, exclude=True)

class MetaAhorroUpdate(MetaAhorroCreate):
    monto_actual: None = Field(default=None, exclude=True)

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
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        return v


class Transaccion(MongoBaseModel, TransaccionBase):
    _id: str
    class Config:
        from_attributes = True


class GastoCreate(TransaccionBase):
    usuario_id: None = Field(default=None, exclude=True)
    categoria_id: str

class GastoGet(MongoBaseModel, TransaccionBase):
    _id: str
    usuario_id: str = Field(exclude=True)
    categoria_id: str

class Gasto(Transaccion):
    categoria_id: str

class IngresoCreate(TransaccionBase):
    meta_id: str
    usuario_id: None = Field(default=None, exclude=True)

class Ingreso(Transaccion):
    meta_id: str

class ResumenMensualBase(BaseModel):
    usuario_id: str
    fecha: datetime
    total_ingresos: float
    total_gastos: float
    balance: float

    @field_validator('fecha')
    def convert_date_to_datetime(cls, v):
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        return v


class ResumenMensual(MongoBaseModel, ResumenMensualBase):
    _id: str
    class Config:
        from_attributes = True