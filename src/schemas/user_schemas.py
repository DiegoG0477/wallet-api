from pydantic import BaseModel
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