from pydantic import BaseModel, Field
from datetime import date

class UsuarioBase(BaseModel):
    correo: str
    contrasena: str
    fecha_registro: date
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    pais_id: int
    estado_id: int
    direccion: str

class Usuario(UsuarioBase):
    id: str
    class Config:
        from_attributes = True

class UsuarioGet(UsuarioBase):
    salario: float
    divisa: str
    balance_objetivo: float
    gasto_limite: float

    contrasena: str = Field(exclude=True)

class UsuarioUpdate(UsuarioGet):
    fecha_registro: None = Field(default=None, exclude=True)
    contrasena: None = Field(default=None, exclude=True)