from pydantic import BaseModel

class EstadoGet(BaseModel):
    id: int
    nombre: str
    pais: str

class PaisGet(BaseModel):
    id: int
    nombre: str