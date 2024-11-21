from pydantic import BaseModel

class EstadoGet(BaseModel):
    id: int
    nombre: str
    pais: str

class EstadoBase(BaseModel):
    nombre: str
    pais_id: str

class Estado(EstadoBase):
    id: int
    class Config:
        from_attributes = True

class PaisBase(BaseModel):
    nombre: str

class Pais(PaisBase):
    id: int
    class Config:
        from_attributes = True